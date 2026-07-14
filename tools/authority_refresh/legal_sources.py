"""Deterministic parsers for official legal-authority discovery sources.

The parsers in this module only normalize publisher-provided discovery metadata.
They deliberately label every result ``discovered`` and never decide whether a
source is binding, effective, applicable, superseded, or legally sufficient.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree


REQUIRED_ITEM_FIELDS = (
    "external_id",
    "title",
    "official_url",
    "published_at",
    "effective_at",
    "status",
    "metadata",
)


class SourceParseError(ValueError):
    """Raised when an official source payload or parser configuration is invalid."""


def parse(
    payload: bytes,
    source: dict[str, Any],
    fetched_at: str,
    final_url: str,
) -> list[dict[str, Any]]:
    """Parse one fetched payload using the adapter declared by ``source``.

    URL allowlisting happens inside every adapter. A publisher link that does not
    resolve to HTTPS on an explicitly allowed host is omitted from the results.
    """

    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if not isinstance(source, dict):
        raise TypeError("source must be a dictionary")
    if not _clean_text(fetched_at):
        raise SourceParseError("fetched_at is required")
    if not _clean_text(final_url):
        raise SourceParseError("final_url is required")

    adapter = _clean_text(source.get("adapter"))
    parser = _ADAPTERS.get(adapter)
    if parser is None:
        supported = ", ".join(sorted(_ADAPTERS))
        raise SourceParseError(
            f"unsupported legal source adapter {adapter!r}; supported: {supported}"
        )

    _allowed_hosts(source)
    items = parser(payload, source, fetched_at, final_url)
    return _deduplicate(items)


def _parse_ecfr_titles_json(
    payload: bytes,
    source: dict[str, Any],
    fetched_at: str,
    final_url: str,
) -> list[dict[str, Any]]:
    data = _load_json(payload)
    if not isinstance(data, dict) or not isinstance(data.get("titles"), list):
        raise SourceParseError("eCFR payload must contain a titles array")

    filters = source.get("filters", {})
    if filters is None:
        filters = {}
    if not isinstance(filters, dict):
        raise SourceParseError("eCFR filters must be an object")

    configured_numbers = filters.get("title_numbers")
    title_numbers: set[int] | None = None
    if configured_numbers is not None:
        if not isinstance(configured_numbers, list):
            raise SourceParseError("eCFR title_numbers must be an array")
        try:
            title_numbers = {int(number) for number in configured_numbers}
        except (TypeError, ValueError) as exc:
            raise SourceParseError("eCFR title_numbers must contain integers") from exc

    include_reserved = bool(filters.get("include_reserved", False))
    url_template = source.get(
        "item_url_template", "https://www.ecfr.gov/current/title-{title_number}"
    )
    if not isinstance(url_template, str):
        raise SourceParseError("eCFR item_url_template must be a string")

    items: list[dict[str, Any]] = []
    for index, record in enumerate(data["titles"]):
        if not isinstance(record, dict):
            raise SourceParseError(f"eCFR title at index {index} is not an object")
        number = record.get("number")
        if isinstance(number, bool):
            raise SourceParseError(f"eCFR title at index {index} has an invalid number")
        try:
            title_number = int(number)
        except (TypeError, ValueError) as exc:
            raise SourceParseError(
                f"eCFR title at index {index} has an invalid number"
            ) from exc
        if title_number < 1:
            raise SourceParseError(f"eCFR title at index {index} has an invalid number")
        if title_numbers is not None and title_number not in title_numbers:
            continue

        reserved = bool(record.get("reserved", False))
        if reserved and not include_reserved:
            continue
        name = _clean_text(record.get("name"))
        if not name:
            raise SourceParseError(f"eCFR title {title_number} is missing its name")

        try:
            candidate_url = url_template.format(title_number=title_number)
        except (KeyError, ValueError) as exc:
            raise SourceParseError("invalid eCFR item_url_template") from exc
        official_url = _canonical_allowed_url(candidate_url, final_url, source)
        if official_url is None:
            continue

        latest_issue_date = _clean_text(record.get("latest_issue_date"))
        metadata = _base_metadata("ecfr_titles_json", fetched_at, final_url)
        metadata.update(
            {
                "title_number": title_number,
                "reserved": reserved,
                "latest_amended_on": _clean_text(record.get("latest_amended_on"))
                or None,
                "latest_issue_date": latest_issue_date or None,
                "up_to_date_as_of": _clean_text(record.get("up_to_date_as_of"))
                or None,
            }
        )
        items.append(
            _item(
                external_id=f"title-{title_number}",
                title=f"{title_number} CFR — {name}",
                official_url=official_url,
                published_at=_normalize_temporal(latest_issue_date),
                effective_at=None,
                metadata=metadata,
            )
        )
    return items


def _parse_rss_atom(
    payload: bytes,
    source: dict[str, Any],
    fetched_at: str,
    final_url: str,
) -> list[dict[str, Any]]:
    lowered = payload.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise SourceParseError("XML document type and entity declarations are not allowed")
    try:
        root = ElementTree.fromstring(payload)
    except (ElementTree.ParseError, ValueError) as exc:
        raise SourceParseError("RSS/Atom payload is not well-formed XML") from exc

    root_name = _local_name(root.tag).lower()
    if root_name == "feed":
        feed_format = "atom"
        record_name = "entry"
    elif root_name in {"rss", "rdf"}:
        feed_format = "rss"
        record_name = "item"
    else:
        raise SourceParseError("payload root is not RSS, RDF, or Atom")

    records = [node for node in root.iter() if _local_name(node.tag) == record_name]
    items: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        raw_link = _feed_link(record)
        official_url = _canonical_allowed_url(raw_link, final_url, source)
        if official_url is None or not _link_matches_filters(official_url, source):
            continue

        external_id = _first_element_text(record, ("guid", "id")) or official_url
        external_id = _clean_text(external_id)
        if not external_id:
            raise SourceParseError(f"feed item at index {index} has no stable identifier")
        title = _first_element_text(record, ("title",)) or external_id
        title = _clean_text(title)

        published_raw = _first_element_text(
            record, ("pubDate", "published", "date", "updated")
        )
        updated_raw = _first_element_text(record, ("updated",))
        metadata = _base_metadata("rss_atom", fetched_at, final_url)
        metadata.update(
            {
                "feed_format": feed_format,
                "publisher_published_at": _clean_text(published_raw) or None,
                "publisher_updated_at": _clean_text(updated_raw) or None,
            }
        )
        items.append(
            _item(
                external_id=external_id,
                title=title,
                official_url=official_url,
                published_at=_normalize_temporal(published_raw),
                effective_at=None,
                metadata=metadata,
            )
        )
    return items


def _parse_official_html_index(
    payload: bytes,
    source: dict[str, Any],
    fetched_at: str,
    final_url: str,
) -> list[dict[str, Any]]:
    text = _decode_utf8(payload, "HTML")
    collector = _AnchorCollector()
    try:
        collector.feed(text)
        collector.close()
    except (ValueError, AssertionError) as exc:
        raise SourceParseError("official HTML index could not be parsed") from exc

    items: list[dict[str, Any]] = []
    for href, anchor_text, title_attribute in collector.links:
        official_url = _canonical_allowed_url(href, final_url, source)
        if official_url is None or not _link_matches_filters(official_url, source):
            continue
        title = _clean_text(anchor_text) or _clean_text(title_attribute)
        if not title:
            title = _title_from_url(official_url)
        metadata = _base_metadata("official_html_index", fetched_at, final_url)
        metadata["anchor_title"] = _clean_text(title_attribute) or None
        items.append(
            _item(
                external_id=official_url,
                title=title,
                official_url=official_url,
                published_at=None,
                effective_at=None,
                metadata=metadata,
            )
        )
    return items


def _parse_official_json_records(
    payload: bytes,
    source: dict[str, Any],
    fetched_at: str,
    final_url: str,
) -> list[dict[str, Any]]:
    data = _load_json(payload)
    records_path = _clean_text(source.get("records_path"))
    records = _get_path(data, records_path) if records_path else data
    if not isinstance(records, list):
        raise SourceParseError("official JSON records payload must resolve to an array")

    field_map = source.get("field_map")
    if not isinstance(field_map, dict):
        raise SourceParseError("official JSON records source requires field_map")
    strict_records = bool(source.get("strict_records", True))
    metadata_fields = source.get("metadata_fields", [])
    if not isinstance(metadata_fields, list) or not all(
        isinstance(field, str) for field in metadata_fields
    ):
        raise SourceParseError("metadata_fields must be an array of strings")

    items: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            if strict_records:
                raise SourceParseError(f"JSON record at index {index} is not an object")
            continue

        external_id = _mapped_text(record, field_map, "external_id")
        title = _mapped_text(record, field_map, "title")
        raw_url = _mapped_text(record, field_map, "official_url")
        if not raw_url:
            raw_url = _render_item_url(source.get("item_url_template"), record)

        if not external_id or not title or not raw_url:
            if strict_records:
                raise SourceParseError(
                    f"JSON record at index {index} lacks an external ID, title, or URL"
                )
            continue
        official_url = _canonical_allowed_url(raw_url, final_url, source)
        if official_url is None or not _link_matches_filters(official_url, source):
            continue

        published_raw = _mapped_text(record, field_map, "published_at")
        effective_raw = _mapped_text(record, field_map, "effective_at")
        publisher_status = _mapped_text(record, field_map, "publisher_status")
        metadata = _base_metadata("official_json_records", fetched_at, final_url)
        metadata.update(
            {
                "publisher_status": publisher_status or None,
                "publisher_published_at": published_raw or None,
                "publisher_effective_at": effective_raw or None,
            }
        )
        for field in metadata_fields:
            value = _get_path(record, field)
            if value is not None:
                metadata[field.replace(".", "_")] = value

        items.append(
            _item(
                external_id=external_id,
                title=title,
                official_url=official_url,
                published_at=_normalize_temporal(published_raw),
                effective_at=_normalize_temporal(effective_raw),
                metadata=metadata,
            )
        )
    return items


def _parse_kansas_legislature_json(
    payload: bytes,
    source: dict[str, Any],
    fetched_at: str,
    final_url: str,
) -> list[dict[str, Any]]:
    """Normalize Kansas Legislature API records without inferring bill effect."""

    configured = dict(source)
    configured.setdefault("records_path", "results")
    configured.setdefault("strict_records", True)
    configured.setdefault(
        "field_map",
        {
            "external_id": ["bill_no", "measure_id", "id", "kpid", "slug"],
            "title": ["short_title", "long_title", "title", "bill_no"],
            "official_url": ["web_url", "url", "href", "document_url"],
            "published_at": ["rev_date", "action_date", "date", "updated_at"],
            "effective_at": ["effective_date"],
            "publisher_status": ["status", "current_status", "action"],
        },
    )
    configured.setdefault(
        "metadata_fields",
        ["bill_no", "leg_type", "session", "version", "doc_type"],
    )
    items = _parse_official_json_records(payload, configured, fetched_at, final_url)

    # A measure can have multiple official versions. Include the version in the
    # external identifier when the publisher supplied one so discovery does not
    # collapse enrolled and earlier bill text into a single record.
    for item in items:
        version = item["metadata"].get("version") or item["metadata"].get("doc_type")
        if version:
            item["external_id"] = f"{item['external_id']}:{_clean_text(version)}"
        item["metadata"]["adapter"] = "kansas_legislature_json"
    return items


def _item(
    *,
    external_id: str,
    title: str,
    official_url: str,
    published_at: str | None,
    effective_at: str | None,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "external_id": _clean_text(external_id),
        "title": _clean_text(title),
        "official_url": official_url,
        "published_at": published_at,
        "effective_at": effective_at,
        "status": "discovered",
        "metadata": metadata,
    }


def _base_metadata(adapter: str, fetched_at: str, final_url: str) -> dict[str, Any]:
    return {
        "adapter": adapter,
        "fetched_at": _clean_text(fetched_at),
        # Response query strings are intentionally omitted because API clients
        # may inject credentials into them at request time.
        "source_response_url": _response_url_without_query(final_url),
    }


def _response_url_without_query(value: str) -> str | None:
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError:
        return None
    host = (parts.hostname or "").lower().rstrip(".")
    if parts.scheme.lower() != "https" or not host or port not in (None, 443):
        return None
    return urlunsplit(("https", host, parts.path or "/", "", ""))


def _load_json(payload: bytes) -> Any:
    text = _decode_utf8(payload, "JSON")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SourceParseError("payload is not valid JSON") from exc


def _decode_utf8(payload: bytes, label: str) -> str:
    try:
        return payload.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise SourceParseError(f"{label} payload is not valid UTF-8") from exc


def _allowed_hosts(source: Mapping[str, Any]) -> frozenset[str]:
    configured = source.get("allowed_hosts")
    if not isinstance(configured, list) or not configured:
        raise SourceParseError("source allowed_hosts must be a non-empty array")
    hosts: set[str] = set()
    for value in configured:
        if not isinstance(value, str):
            raise SourceParseError("source allowed_hosts entries must be strings")
        host = value.strip().lower().rstrip(".")
        if not host or "/" in host or ":" in host:
            raise SourceParseError(f"invalid allowed host {value!r}")
        hosts.add(host)
    return frozenset(hosts)


def _canonical_allowed_url(
    raw_url: Any,
    base_url: str,
    source: Mapping[str, Any],
) -> str | None:
    candidate = _clean_text(raw_url)
    if not candidate:
        return None
    try:
        absolute = urljoin(base_url, candidate)
        parts = urlsplit(absolute)
        port = parts.port
    except ValueError:
        return None
    host = (parts.hostname or "").lower().rstrip(".")
    if (
        parts.scheme.lower() != "https"
        or not host
        or parts.username is not None
        or parts.password is not None
        or port not in (None, 443)
        or host not in _allowed_hosts(source)
    ):
        return None
    path = parts.path or "/"
    return urlunsplit(("https", host, path, parts.query, ""))


def _link_matches_filters(url: str, source: Mapping[str, Any]) -> bool:
    filters = source.get("link_filter", {})
    if filters is None:
        return True
    if not isinstance(filters, dict):
        raise SourceParseError("link_filter must be an object")
    includes = _regex_list(filters.get("include_patterns", []), "include_patterns")
    excludes = _regex_list(filters.get("exclude_patterns", []), "exclude_patterns")
    if includes and not any(pattern.search(url) for pattern in includes):
        return False
    return not any(pattern.search(url) for pattern in excludes)


def _regex_list(values: Any, label: str) -> list[re.Pattern[str]]:
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise SourceParseError(f"{label} must be an array of strings")
    try:
        return [re.compile(value, re.IGNORECASE) for value in values]
    except re.error as exc:
        raise SourceParseError(f"{label} contains an invalid regular expression") from exc


def _deduplicate(items: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    for item in items:
        missing = [field for field in REQUIRED_ITEM_FIELDS if field not in item]
        if missing:
            raise SourceParseError(f"normalized item is missing fields: {', '.join(missing)}")
        if item["status"] != "discovered":
            raise SourceParseError("discovery parsers may only emit status='discovered'")

    ordered = sorted(
        items,
        key=lambda item: (
            str(item["external_id"]).casefold(),
            str(item["official_url"]),
            json.dumps(item["metadata"], sort_keys=True, separators=(",", ":")),
        ),
    )
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in ordered:
        external_id = str(item["external_id"])
        official_url = str(item["official_url"])
        if external_id in seen_ids or official_url in seen_urls:
            continue
        seen_ids.add(external_id)
        seen_urls.add(official_url)
        unique.append(item)
    return unique


def _normalize_temporal(value: Any) -> str | None:
    text = _clean_text(value)
    if not text:
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        try:
            datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            return None
        return text

    parsed: datetime | None = None
    try:
        parsed = parsedate_to_datetime(text)
    except (TypeError, ValueError, OverflowError):
        pass
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.isoformat(timespec="seconds")
    return (
        parsed.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _local_name(tag: Any) -> str:
    text = str(tag)
    return text.rsplit("}", 1)[-1].rsplit(":", 1)[-1]


def _first_element_text(element: ElementTree.Element, names: Sequence[str]) -> str:
    wanted = set(names)
    for node in element.iter():
        if node is not element and _local_name(node.tag) in wanted:
            text = _clean_text("".join(node.itertext()))
            if text:
                return text
    return ""


def _feed_link(record: ElementTree.Element) -> str:
    candidates: list[tuple[int, str]] = []
    for node in record.iter():
        if node is record or _local_name(node.tag) != "link":
            continue
        href = _clean_text(node.attrib.get("href"))
        rel = _clean_text(node.attrib.get("rel")).lower()
        if href:
            priority = 0 if rel in {"", "alternate"} else 1
            candidates.append((priority, href))
        else:
            text = _clean_text("".join(node.itertext()))
            if text:
                candidates.append((0, text))
    if not candidates:
        return ""
    return sorted(candidates, key=lambda candidate: candidate[0])[0][1]


def _get_path(value: Any, path: str) -> Any:
    current = value
    if not path:
        return current
    for component in path.split("."):
        if not isinstance(current, Mapping) or component not in current:
            return None
        current = current[component]
    return current


def _field_paths(field_map: Mapping[str, Any], field: str) -> list[str]:
    configured = field_map.get(field, [])
    if isinstance(configured, str):
        return [configured]
    if isinstance(configured, list) and all(isinstance(path, str) for path in configured):
        return configured
    raise SourceParseError(f"field_map.{field} must be a string or array of strings")


def _mapped_text(
    record: Mapping[str, Any], field_map: Mapping[str, Any], field: str
) -> str:
    for path in _field_paths(field_map, field):
        value = _get_path(record, path)
        text = _clean_text(value)
        if text:
            return text
    return ""


def _render_item_url(template: Any, record: Mapping[str, Any]) -> str:
    if template is None:
        return ""
    if not isinstance(template, str):
        raise SourceParseError("item_url_template must be a string")
    scalar_values = {
        key: _clean_text(value)
        for key, value in record.items()
        if isinstance(value, (str, int, float)) and not isinstance(value, bool)
    }
    try:
        return template.format_map(scalar_values)
    except (KeyError, ValueError) as exc:
        raise SourceParseError("item_url_template references a missing field") from exc


def _title_from_url(url: str) -> str:
    path = urlsplit(url).path.rstrip("/")
    final_component = path.rsplit("/", 1)[-1] if path else urlsplit(url).hostname or url
    return re.sub(r"[-_]+", " ", final_component).strip() or url


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, (str, int, float)) or isinstance(value, bool):
        return ""
    return " ".join(str(value).split())


class _AnchorCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str, str]] = []
        self._anchor: dict[str, Any] | None = None
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered in {"script", "style", "template"}:
            self._ignored_depth += 1
            return
        if self._ignored_depth or lowered != "a":
            return
        attributes = {key.lower(): value or "" for key, value in attrs}
        self._anchor = {
            "href": attributes.get("href", ""),
            "title": attributes.get("title", ""),
            "text": [],
        }

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"script", "style", "template"}:
            if self._ignored_depth:
                self._ignored_depth -= 1
            return
        if self._ignored_depth or lowered != "a" or self._anchor is None:
            return
        self.links.append(
            (
                self._anchor["href"],
                "".join(self._anchor["text"]),
                self._anchor["title"],
            )
        )
        self._anchor = None

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and self._anchor is not None:
            self._anchor["text"].append(data)


_ADAPTERS: dict[
    str,
    Callable[[bytes, dict[str, Any], str, str], list[dict[str, Any]]],
] = {
    "ecfr_titles_json": _parse_ecfr_titles_json,
    "rss_atom": _parse_rss_atom,
    "official_html_index": _parse_official_html_index,
    "official_json_records": _parse_official_json_records,
    "kansas_legislature_json": _parse_kansas_legislature_json,
}
