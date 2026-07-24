"""Metadata-only discovery adapters for official accounting and tax indexes.

These adapters identify candidate publications for human review. They do not
copy FASB Codification content, decide GAAP applicability, or turn an index
entry into an approved accounting conclusion.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree


class SourceConfigurationError(ValueError):
    """Raised when a source could permit unsafe or unlicensed discovery."""


class PayloadParseError(ValueError):
    """Raised when a structured source payload cannot be parsed safely."""


_REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "publisher",
    "jurisdiction",
    "authority_type",
    "discovery_url",
    "adapter",
    "storage_policy",
    "cadence",
    "critical",
    "allowed_hosts",
}
_FASB_STORAGE_POLICIES = {"metadata-only", "licensed-no-store"}
_ITEM_FIELDS = {
    "external_id",
    "title",
    "official_url",
    "published_at",
    "effective_at",
    "status",
    "metadata",
}
_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|"
    "November|December"
)
_EXACT_DATE_RE = re.compile(
    rf"\b(?:{_MONTHS})\s+\d{{1,2}},\s+\d{{4}}\b|\b\d{{4}}-\d{{2}}-\d{{2}}\b"
)
_ASU_RE = re.compile(
    r"\b(?:Accounting\s+Standards\s+Update|ASU|Update)\s+"
    r"(?P<number>20\d{2}-\d{2})\b",
    re.IGNORECASE,
)
_IRB_RE = re.compile(
    r"\bInternal\s+Revenue\s+Bulletin\s*:?\s*(?P<number>20\d{2}-\d{1,2})\b",
    re.IGNORECASE,
)
_KDOR_NOTICE_RE = re.compile(
    r"\bNotice\s+(?P<number>\d{2,4}-\d{1,2})\b", re.IGNORECASE
)
_KDOR_RULING_RE = re.compile(
    r"\b(?:Revised\s+)?Revenue\s+Ruling\s+(?P<number>[0-9-]+)\b",
    re.IGNORECASE,
)
_ASC_PARAGRAPH_RE = re.compile(r"\bASC\s+\d{3}-\d{2}-\d{2}-\d+\b", re.IGNORECASE)


@dataclass
class _Anchor:
    href: str
    text_parts: list[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return _clean_text(" ".join(self.text_parts))


@dataclass
class _Cell:
    text_parts: list[str] = field(default_factory=list)
    anchors: list[_Anchor] = field(default_factory=list)

    @property
    def text(self) -> str:
        return _clean_text(" ".join(self.text_parts))


class _IndexHTMLParser(HTMLParser):
    """Collect links and table cells without constructing or storing a DOM."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[_Anchor] = []
        self.rows: list[list[_Cell]] = []
        self._anchor: _Anchor | None = None
        self._row: list[_Cell] | None = None
        self._cell: _Cell | None = None
        self._ignored_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "template"}:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag == "tr":
            self._finish_anchor()
            self._finish_cell()
            self._finish_row()
            self._row = []
        elif tag in {"td", "th"}:
            self._finish_anchor()
            self._finish_cell()
            if self._row is None:
                self._row = []
            self._cell = _Cell()
        elif tag == "a":
            # A new link also terminates a malformed, unclosed prior link.
            self._finish_anchor()
            href = dict(attrs).get("href") or ""
            self._anchor = _Anchor(href=href)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "template"}:
            if self._ignored_depth:
                self._ignored_depth -= 1
            return
        if self._ignored_depth:
            return
        if tag == "a":
            self._finish_anchor()
        elif tag in {"td", "th"}:
            self._finish_anchor()
            self._finish_cell()
        elif tag == "tr":
            self._finish_anchor()
            self._finish_cell()
            self._finish_row()

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        if self._anchor is not None:
            self._anchor.text_parts.append(data)
        if self._cell is not None:
            self._cell.text_parts.append(data)

    def finish(self) -> None:
        self._finish_anchor()
        self._finish_cell()
        self._finish_row()

    def _finish_anchor(self) -> None:
        if self._anchor is None:
            return
        if self._anchor.href and self._anchor.text:
            self.anchors.append(self._anchor)
            if self._cell is not None:
                self._cell.anchors.append(self._anchor)
        self._anchor = None

    def _finish_cell(self) -> None:
        if self._cell is None:
            return
        if self._row is None:
            self._row = []
        self._row.append(self._cell)
        self._cell = None

    def _finish_row(self) -> None:
        if self._row:
            self.rows.append(self._row)
        self._row = None


def parse(
    payload: bytes,
    source: dict[str, Any],
    fetched_at: str,
    final_url: str,
) -> list[dict[str, Any]]:
    """Parse one configured source into bounded metadata-only candidates.

    Off-host links are ignored. An off-host fetch result, unsafe FASB storage
    policy, unsupported adapter, or oversized payload fails closed.
    """

    _validate_source(source, final_url)
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if not isinstance(fetched_at, str) or not fetched_at.strip():
        raise SourceConfigurationError("fetched_at must be a non-empty string")

    request = source.get("request", {})
    max_bytes = request.get("max_bytes", 5_000_000)
    if not isinstance(max_bytes, int) or max_bytes <= 0:
        raise SourceConfigurationError("request.max_bytes must be a positive integer")
    if len(payload) > max_bytes:
        raise PayloadParseError(
            f"payload is {len(payload)} bytes; configured maximum is {max_bytes}"
        )

    adapter = source["adapter"]
    try:
        parser = _ADAPTERS[adapter]
    except KeyError as exc:
        raise SourceConfigurationError(f"unsupported accounting adapter: {adapter}") from exc

    items = parser(payload, source, final_url)
    return _deduplicate_and_validate(items, source)


def _validate_source(source: dict[str, Any], final_url: str) -> None:
    if not isinstance(source, dict):
        raise SourceConfigurationError("source must be an object")
    missing = sorted(_REQUIRED_SOURCE_FIELDS - source.keys())
    if missing:
        raise SourceConfigurationError(
            "source is missing required fields: " + ", ".join(missing)
        )

    allowed_hosts = source["allowed_hosts"]
    if (
        not isinstance(allowed_hosts, list)
        or not allowed_hosts
        or not all(isinstance(host, str) and host.strip() for host in allowed_hosts)
    ):
        raise SourceConfigurationError("allowed_hosts must be a non-empty string list")

    discovery_url = source["discovery_url"]
    if _canonical_official_url(discovery_url, discovery_url, allowed_hosts) is None:
        raise SourceConfigurationError("discovery_url is not an allowlisted HTTPS URL")
    if _canonical_official_url(final_url, discovery_url, allowed_hosts) is None:
        raise SourceConfigurationError("final_url is not an allowlisted HTTPS URL")

    discovery_host = (
        (urlsplit(discovery_url).hostname or "").lower().rstrip(".")
    )
    publisher = str(source["publisher"]).lower()
    is_fasb = (
        "fasb" in publisher
        or discovery_host == "fasb.org"
        or discovery_host.endswith(".fasb.org")
    )
    if is_fasb and source["storage_policy"] not in _FASB_STORAGE_POLICIES:
        raise SourceConfigurationError(
            "FASB discovery is restricted to metadata-only or licensed-no-store"
        )
    if is_fasb and discovery_host == "asc.fasb.org":
        raise SourceConfigurationError(
            "the licensed FASB Codification application is not a discovery index"
        )


def _parse_html(payload: bytes) -> _IndexHTMLParser:
    parser = _IndexHTMLParser()
    try:
        parser.feed(payload.decode("utf-8-sig", errors="replace"))
        parser.close()
        parser.finish()
    except (ValueError, AssertionError) as exc:
        raise PayloadParseError(f"HTML index could not be parsed: {exc}") from exc
    return parser


def _parse_fasb_asu_index(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    for anchor in document.anchors:
        match = _ASU_RE.search(anchor.text)
        official_url = _official_link(anchor.href, final_url, source)
        if match is None or official_url is None:
            continue
        number = match.group("number")
        items.append(
            _item(
                external_id=f"FASB-ASU-{number}",
                title=_safe_fasb_title(anchor.text),
                official_url=official_url,
                status="discovered",
                metadata={
                    "document_type": "accounting-standards-update",
                    "asu_number": number,
                    "publisher_status": "issued",
                },
            )
        )
    return items


def _parse_fasb_effective_dates(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    row_numbers: set[str] = set()

    for row in document.rows:
        if not row:
            continue
        match = _ASU_RE.search(row[0].text)
        if match is None:
            continue
        # FASB currently presents the document link in a separate Action cell.
        # Search the complete row so harmless table-column changes do not hide
        # effective-date evidence.
        official_url = next(
            (
                link
                for cell in row
                for anchor in cell.anchors
                if (link := _official_link(anchor.href, final_url, source)) is not None
            ),
            None,
        )
        if official_url is None:
            continue

        number = match.group("number")
        row_numbers.add(number)
        issued_label = row[1].text[:80] if len(row) > 1 else ""
        effective_text = row[2].text if len(row) > 2 else ""
        effective_mentions = _extract_exact_dates(effective_text)
        metadata: dict[str, Any] = {
            "document_type": "asu-effective-date-reference",
            "asu_number": number,
            "effective_date_mentions": effective_mentions,
            "entity_specific_dates_present": bool(
                re.search(
                    r"public business entit|entities other than|all entities",
                    effective_text,
                    re.IGNORECASE,
                )
            ),
        }
        if issued_label:
            metadata["issued_label"] = issued_label
        items.append(
            _item(
                external_id=f"FASB-ASU-EFFECTIVE-{number}",
                title=_safe_fasb_title(row[0].text),
                official_url=official_url,
                published_at=_parse_exact_date(issued_label),
                # Multiple entity classes and fiscal periods are common. A
                # reviewer, not this parser, selects an applicable date.
                effective_at=None,
                status="discovered",
                metadata=metadata,
            )
        )

    # Keep discovery useful if the publisher changes table markup. The
    # fallback intentionally omits effective-date claims.
    for anchor in document.anchors:
        match = _ASU_RE.search(anchor.text)
        if match is None or match.group("number") in row_numbers:
            continue
        official_url = _official_link(anchor.href, final_url, source)
        if official_url is None:
            continue
        number = match.group("number")
        items.append(
            _item(
                external_id=f"FASB-ASU-EFFECTIVE-{number}",
                title=_safe_fasb_title(anchor.text),
                official_url=official_url,
                status="discovered",
                metadata={
                    "document_type": "asu-effective-date-reference",
                    "asu_number": number,
                    "effective_date_mentions": [],
                    "entity_specific_dates_present": False,
                },
            )
        )
    return items


def _parse_fasb_project_index(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    ignored_titles = {
        "current projects",
        "recently completed projects",
        "project resources",
        "project history",
        "issued documents and materials",
    }
    for anchor in document.anchors:
        official_url = _official_link(anchor.href, final_url, source)
        if official_url is None:
            continue
        path = urlsplit(official_url).path.lower().rstrip("/")
        title = _safe_fasb_title(anchor.text)
        if (
            "/projects/current-projects/" not in path
            or path.endswith("current-project-details.html")
            or title.lower() in ignored_titles
        ):
            continue
        slug = _last_path_slug(official_url)
        items.append(
            _item(
                external_id=f"FASB-PROJECT-{slug.upper()}",
                title=title,
                official_url=official_url,
                status="discovered",
                metadata={
                    "document_type": "fasb-project",
                    "project_slug": slug,
                    "publisher_status": "current-project",
                },
            )
        )
    return items


def _parse_fasb_taxonomy_index(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    for anchor in document.anchors:
        official_url = _official_link(anchor.href, final_url, source)
        if official_url is None:
            continue
        haystack = f"{anchor.text} {urlsplit(official_url).path}"
        if not re.search(r"taxonom|xbrl", haystack, re.IGNORECASE):
            continue
        title = _safe_fasb_title(anchor.text)
        if title.lower() in {"fasb taxonomies", "taxonomies"}:
            continue
        year_match = re.search(r"\b(20\d{2})\b", title)
        metadata: dict[str, Any] = {"document_type": "fasb-taxonomy-resource"}
        if year_match:
            metadata["taxonomy_year"] = year_match.group(1)
        items.append(
            _item(
                external_id=_hashed_external_id("FASB-TAXONOMY", official_url),
                title=title,
                official_url=official_url,
                status="discovered",
                metadata=metadata,
            )
        )
    return items


def _parse_irs_irb_index(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    row_dates: dict[str, str | None] = {}
    for row in document.rows:
        if not row:
            continue
        match = _IRB_RE.search(row[0].text)
        if match:
            row_dates[match.group("number")] = (
                _parse_exact_date(row[1].text) if len(row) > 1 else None
            )

    for anchor in document.anchors:
        match = _IRB_RE.search(anchor.text)
        official_url = _official_link(anchor.href, final_url, source)
        if match is None or official_url is None:
            continue
        number = match.group("number")
        items.append(
            _item(
                external_id=f"IRS-IRB-{number}",
                title=anchor.text,
                official_url=official_url,
                published_at=row_dates.get(number),
                status="discovered",
                metadata={
                    "document_type": "internal-revenue-bulletin",
                    "bulletin_number": number,
                },
            )
        )
    return items


def _parse_kansas_revenue_index(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    for anchor in document.anchors:
        official_url = _official_link(anchor.href, final_url, source)
        if official_url is None:
            continue
        notice = _KDOR_NOTICE_RE.search(anchor.text)
        ruling = _KDOR_RULING_RE.search(anchor.text)
        if notice:
            number = notice.group("number")
            document_type = "tax-notice"
            external_id = f"KDOR-NOTICE-{number}"
        elif ruling:
            number = ruling.group("number")
            document_type = "revenue-ruling"
            external_id = f"KDOR-REVENUE-RULING-{number}"
        else:
            continue

        title_lower = anchor.text.lower()
        if "revoked" in title_lower:
            publisher_status = "revoked"
        elif "revised" in title_lower:
            publisher_status = "revised"
        else:
            publisher_status = "published"
        items.append(
            _item(
                external_id=external_id,
                title=anchor.text,
                official_url=official_url,
                status="discovered",
                metadata={
                    "document_type": document_type,
                    "document_number": number,
                    "publisher_status": publisher_status,
                },
            )
        )
    return items


def _parse_treasury_press_index(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    accounting_or_tax = re.compile(
        r"\b(?:tax|taxpayer|taxation|internal revenue|IRS|revenue procedure|"
        r"revenue ruling|accounting|financial reporting)\b",
        re.IGNORECASE,
    )
    for anchor in document.anchors:
        official_url = _official_link(anchor.href, final_url, source)
        if official_url is None:
            continue
        path = urlsplit(official_url).path.lower()
        if "/news/press-releases/" not in path or not accounting_or_tax.search(
            anchor.text
        ):
            continue
        items.append(
            _item(
                external_id=_hashed_external_id("TREASURY-RELEASE", official_url),
                title=anchor.text,
                official_url=official_url,
                status="discovered",
                metadata={"document_type": "treasury-press-release"},
            )
        )
    return items


def _parse_official_index(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    """Parse a configured official HTML index without storing page bodies."""

    match_config = source.get("match", {})
    path_prefixes = match_config.get("path_prefixes", [])
    title_patterns = match_config.get("title_patterns", [])
    if not path_prefixes and not title_patterns:
        raise SourceConfigurationError(
            "official_index requires match.path_prefixes or match.title_patterns"
        )
    try:
        title_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in title_patterns]
    except re.error as exc:
        raise SourceConfigurationError(f"invalid title pattern: {exc}") from exc

    document = _parse_html(payload)
    items: list[dict[str, Any]] = []
    for anchor in document.anchors:
        official_url = _official_link(anchor.href, final_url, source)
        if official_url is None:
            continue
        path = urlsplit(official_url).path
        if path_prefixes and not any(path.startswith(prefix) for prefix in path_prefixes):
            continue
        if title_regexes and not any(regex.search(anchor.text) for regex in title_regexes):
            continue
        items.append(
            _item(
                external_id=_hashed_external_id(source["source_id"].upper(), official_url),
                title=anchor.text,
                official_url=official_url,
                status="discovered",
                metadata={"document_type": "official-index-entry"},
            )
        )
    return items


def _parse_official_feed(
    payload: bytes, source: dict[str, Any], final_url: str
) -> list[dict[str, Any]]:
    """Parse RSS or Atom titles, links, identifiers, and dates only."""

    lowered = payload.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise PayloadParseError("RSS/Atom DTDs and entities are not permitted")
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise PayloadParseError(f"RSS/Atom feed could not be parsed: {exc}") from exc

    feed_format = "atom" if _local_name(root.tag) == "feed" else "rss"
    entry_names = {"entry"} if feed_format == "atom" else {"item"}
    items: list[dict[str, Any]] = []
    for entry in (element for element in root.iter() if _local_name(element.tag) in entry_names):
        title = _xml_child_text(entry, "title")
        official_url = _feed_link(entry, final_url, source)
        if not title or official_url is None:
            continue
        identifier = _xml_child_text(entry, "id") or _xml_child_text(entry, "guid")
        published = (
            _xml_child_text(entry, "published")
            or _xml_child_text(entry, "pubDate")
            or _xml_child_text(entry, "updated")
        )
        id_material = identifier or official_url
        items.append(
            _item(
                external_id=_hashed_external_id(
                    source["source_id"].upper(), id_material
                ),
                title=title,
                official_url=official_url,
                published_at=_parse_feed_date(published),
                status="discovered",
                metadata={"document_type": "official-feed-entry", "feed_format": feed_format},
            )
        )
    return items


def _feed_link(
    entry: ElementTree.Element,
    final_url: str,
    source: dict[str, Any],
) -> str | None:
    for child in entry:
        if _local_name(child.tag) != "link":
            continue
        rel = child.attrib.get("rel", "alternate")
        if rel not in {"alternate", ""}:
            continue
        href = child.attrib.get("href") or (child.text or "")
        official_url = _official_link(href, final_url, source)
        if official_url is not None:
            return official_url
    return None


def _xml_child_text(element: ElementTree.Element, name: str) -> str:
    for child in element:
        if _local_name(child.tag) == name:
            return _clean_text("".join(child.itertext()))
    return ""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _item(
    *,
    external_id: str,
    title: str,
    official_url: str,
    status: str,
    metadata: dict[str, Any],
    published_at: str | None = None,
    effective_at: str | None = None,
) -> dict[str, Any]:
    return {
        "external_id": external_id,
        "title": _clean_text(title)[:500],
        "official_url": official_url,
        "published_at": published_at,
        "effective_at": effective_at,
        "status": status,
        "metadata": metadata,
    }


def _deduplicate_and_validate(
    items: list[dict[str, Any]], source: dict[str, Any]
) -> list[dict[str, Any]]:
    deduplicated: dict[str, dict[str, Any]] = {}
    seen_urls: set[str] = set()
    for item in sorted(
        items,
        key=lambda candidate: (
            str(candidate.get("external_id", "")),
            str(candidate.get("official_url", "")),
            str(candidate.get("title", "")),
        ),
    ):
        if set(item) != _ITEM_FIELDS:
            raise PayloadParseError("adapter emitted an unexpected item shape")
        if not item["external_id"] or not item["title"] or not item["official_url"]:
            continue
        if item["status"] != "discovered":
            raise PayloadParseError("accounting discovery items must remain unreviewed")
        if _official_link(item["official_url"], source["discovery_url"], source) is None:
            continue

        key = item["external_id"]
        existing = deduplicated.get(key)
        if existing is None:
            if item["official_url"] in seen_urls:
                continue
            deduplicated[key] = item
            seen_urls.add(item["official_url"])
            continue
        if existing["published_at"] is None and item["published_at"] is not None:
            existing["published_at"] = item["published_at"]
        if existing["effective_at"] is None and item["effective_at"] is not None:
            existing["effective_at"] = item["effective_at"]
        existing["metadata"].update(
            {key: value for key, value in item["metadata"].items() if value not in (None, "", [])}
        )

    return sorted(
        deduplicated.values(),
        key=lambda item: (item["external_id"], item["official_url"]),
    )


def _official_link(
    href: str, final_url: str, source: dict[str, Any]
) -> str | None:
    return _canonical_official_url(href, final_url, source["allowed_hosts"])


def _canonical_official_url(
    href: str, base_url: str, allowed_hosts: list[str]
) -> str | None:
    if not isinstance(href, str) or not href.strip():
        return None
    candidate = urljoin(base_url, href.strip())
    parsed = urlsplit(candidate)
    if parsed.scheme.lower() != "https" or parsed.username or parsed.password:
        return None
    try:
        if parsed.port not in {None, 443}:
            return None
    except ValueError:
        return None
    host = (parsed.hostname or "").lower().rstrip(".")
    if not _host_is_allowed(host, allowed_hosts):
        return None
    return urlunsplit(("https", parsed.netloc.lower(), parsed.path or "/", parsed.query, ""))


def _host_is_allowed(host: str, allowed_hosts: list[str]) -> bool:
    for raw_allowed in allowed_hosts:
        allowed = raw_allowed.lower().strip().rstrip(".")
        if allowed.startswith("*."):
            suffix = allowed[1:]
            if host.endswith(suffix) and host != suffix[1:]:
                return True
        elif host == allowed:
            return True
    return False


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _safe_fasb_title(value: str) -> str:
    title = _clean_text(value)
    # A malformed link must not absorb licensed paragraph content into a title.
    paragraph = _ASC_PARAGRAPH_RE.search(title)
    if paragraph:
        title = title[: paragraph.start()].rstrip(" -:;")
    return title[:500]


def _extract_exact_dates(value: str) -> list[str]:
    dates = {
        parsed
        for raw in _EXACT_DATE_RE.findall(value)
        if (parsed := _parse_exact_date(raw)) is not None
    }
    return sorted(dates)


def _parse_exact_date(value: str) -> str | None:
    cleaned = _clean_text(value)
    for format_string in ("%m/%d/%Y", "%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, format_string).date().isoformat()
        except ValueError:
            continue
    return None


def _parse_feed_date(value: str) -> str | None:
    cleaned = _clean_text(value)
    if not cleaned:
        return None
    exact = _parse_exact_date(cleaned)
    if exact:
        return exact
    try:
        parsed = parsedate_to_datetime(cleaned)
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _last_path_slug(url: str) -> str:
    raw = urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1]
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug[:120] or hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def _hashed_external_id(prefix: str, value: str) -> str:
    safe_prefix = re.sub(r"[^A-Z0-9]+", "-", prefix.upper()).strip("-")
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:20]
    return f"{safe_prefix}-{digest}"


_Adapter = Callable[[bytes, dict[str, Any], str], list[dict[str, Any]]]
_ADAPTERS: dict[str, _Adapter] = {
    "fasb_asu_index": _parse_fasb_asu_index,
    "fasb_effective_dates": _parse_fasb_effective_dates,
    "fasb_project_index": _parse_fasb_project_index,
    "fasb_taxonomy_index": _parse_fasb_taxonomy_index,
    "irs_irb_index": _parse_irs_irb_index,
    "kansas_revenue_index": _parse_kansas_revenue_index,
    "treasury_press_index": _parse_treasury_press_index,
    "official_index": _parse_official_index,
    "official_feed": _parse_official_feed,
}


__all__ = [
    "PayloadParseError",
    "SourceConfigurationError",
    "parse",
]
