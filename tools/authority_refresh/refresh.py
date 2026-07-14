#!/usr/bin/env python3
"""Run legal/accounting discovery without modifying approved authority content."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

try:  # package import in tests and modules
    from . import accounting_sources, legal_sources
    from .core import AuthorityRefreshError, scan_domain
except ImportError:  # direct `python tools/authority_refresh/refresh.py`
    import accounting_sources  # type: ignore[no-redef]
    import legal_sources  # type: ignore[no-redef]
    from core import AuthorityRefreshError, scan_domain  # type: ignore[no-redef]


DOMAIN_SETTINGS = {
    "legal": {
        "catalog": PACKAGE_DIR / "config" / "legal_sources.json",
        "baseline": REPO_ROOT / "authority" / "snapshots" / "legal.json",
        "parser": legal_sources.parse,
    },
    "accounting": {
        "catalog": PACKAGE_DIR / "config" / "accounting_sources.json",
        "baseline": REPO_ROOT / "authority" / "snapshots" / "accounting.json",
        "parser": accounting_sources.parse,
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--domain",
        choices=["legal", "accounting", "all"],
        default="all",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("authority-refresh-output"),
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        help="Use deterministic offline payloads instead of network requests.",
    )
    parser.add_argument(
        "--run-id",
        default="local",
        help="Audit identifier such as the GitHub Actions run ID.",
    )
    args = parser.parse_args()

    domains = list(DOMAIN_SETTINGS) if args.domain == "all" else [args.domain]
    summaries: dict[str, object] = {}
    exit_code = 0
    try:
        for domain in domains:
            settings = DOMAIN_SETTINGS[domain]
            fixture_dir = args.fixture_dir / domain if args.fixture_dir else None
            candidate, domain_exit = scan_domain(
                domain=domain,
                catalog_path=settings["catalog"],
                baseline_path=settings["baseline"],
                parser=settings["parser"],
                output_dir=args.output_dir,
                run_id=args.run_id,
                fixture_dir=fixture_dir,
                impact_crosswalk_path=REPO_ROOT / "authority" / "impact_crosswalk.json",
            )
            summaries[domain] = {
                "status": candidate["status"],
                "counts": candidate["counts"],
                "candidate_sha256": candidate["candidate_sha256"],
            }
            exit_code = max(exit_code, domain_exit)
    except AuthorityRefreshError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    print(json.dumps(summaries, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
