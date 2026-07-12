#!/usr/bin/env python3
"""Fetch official chapter PDFs from Overland Park's enCodePlus exporter."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


BASE = "https://online.encodeplus.com/regs/overlandpark-ks"
PID = 561


SOURCES = {
    "005.024": "OPMC_5.75_Rental_Licensing_and_Inspection.pdf",
    "006": "OPMC_Title_6_Animals.pdf",
    "007.001": "OPMC_7.01_Code_Enforcement.pdf",
    "007.002": "OPMC_7.04_Nuisances.pdf",
    "007.003": "OPMC_7.08_Noise.pdf",
    "007.004": "OPMC_7.16_Trees_and_Shrubs.pdf",
    "007.005": "OPMC_7.20_Weeds.pdf",
    "007.006": "OPMC_7.22_Vehicle_Parking_and_Storage.pdf",
    "007.007": "OPMC_7.25_Property_Maintenance.pdf",
    "007.008": "OPMC_7.28_Immediate_Hazards.pdf",
    "007.009": "OPMC_7.32_Rat_Control.pdf",
    "007.010": "OPMC_7.36_Solid_Waste_and_Recyclables.pdf",
    "007.011": "OPMC_7.54_Excavation_Grading_and_Drainage.pdf",
    "007.013": "OPMC_7.58_Stormwater_Pollution.pdf",
    "008.001": "OPMC_8.10_Civil_Rights.pdf",
    "012.008": "OPMC_12.21_Private_Towing.pdf",
    "016.004": "OPMC_16.300_Building_Code_Amendments.pdf",
    "016.005": "OPMC_16.305_Existing_Building_Code_Amendments.pdf",
    "016.007": "OPMC_16.320_Fire_Code_Amendments.pdf",
    "016.008": "OPMC_16.330_Plumbing_Code_Amendments.pdf",
    "016.009": "OPMC_16.340_Mechanical_Code_Amendments.pdf",
    "016.010": "OPMC_16.350_Fuel_Gas_Code_Amendments.pdf",
    "016.011": "OPMC_16.360_Electrical_Code_Amendments.pdf",
    "016.012": "OPMC_16.370_Energy_Code_Amendments.pdf",
    "018.002": "OPMC_18.110_Definitions.pdf",
    "018.015": "OPMC_18.210_R3_Garden_Apartment_District.pdf",
    "018.034": "OPMC_18.390_Accessory_Uses_and_Structures.pdf",
    "018.037": "OPMC_18.410_Nonconforming_Situations.pdf",
    "018.039": "OPMC_18.430_Parking_and_Loading.pdf",
}


def request(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 GH-Real-Estate-Legal-Source-Pack/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def fetch_one(item: tuple[str, str], output_dir: Path) -> dict[str, object]:
    tocid, filename = item
    component_url = (
        f"{BASE}/component.aspx?"
        + urllib.parse.urlencode(
            {
                "name": "export2doc",
                "doctype": "p",
                "pid": PID,
                "tocid": tocid,
                "catid": 0,
            }
        )
    )

    result: dict[str, object] | None = None
    for _ in range(12):
        payload = request(component_url)
        result = json.loads(payload.decode("utf-8"))
        if result.get("Failed"):
            raise RuntimeError(f"Export failed for {tocid}: {result.get('Msg')}")
        if result.get("Ready"):
            break
        time.sleep(2)
    else:
        raise TimeoutError(f"Export was not ready for {tocid}")

    remote_file = str(result["File"])
    download_url = (
        f"{BASE}/export2doc.aspx?"
        + urllib.parse.urlencode(
            {"pdf": 1, "tocid": tocid, "file": remote_file}
        )
    )
    pdf = request(download_url, timeout=120)
    if not pdf.startswith(b"%PDF-"):
        preview = re.sub(rb"\s+", b" ", pdf[:200])
        raise ValueError(f"Non-PDF response for {tocid}: {preview!r}")

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / filename
    destination.write_bytes(pdf)
    return {
        "tocid": tocid,
        "filename": filename,
        "bytes": len(pdf),
        "source_url": f"{BASE}/export2doc.aspx?pdf=1&tocid={tocid}",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(fetch_one, item, args.output_dir): item[0]
            for item in SOURCES.items()
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"Fetched {result['tocid']} -> {result['filename']}", flush=True)

    results.sort(key=lambda entry: str(entry["tocid"]))
    manifest = args.output_dir / "encodeplus_manifest.json"
    manifest.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {manifest}")


if __name__ == "__main__":
    main()
