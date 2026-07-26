#!/usr/bin/env python3
"""Fix CLEWs Global transmission generation to use mapped grid-node codes."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


BUGGY = '''    for i in data["EndUseFuels"]:
        fuel_list = data["EndUseFuels"][i]
        for j in region_codes:
            fuel_list.append(f"ELC{region_codes[j]}02")
        data["EndUseFuels"][i] = fuel_list
    data["TransformationTechnologies"] = []
    for j in region_codes:
        data["TransformationTechnologies"].append([
            'PWRTRNA01', f'ELC{j}01', '1.11', f'ELC{j}02', '1', 'Power transmission', '1'])
'''

FIXED = '''    grid_regions = list(dict.fromkeys(region_codes.values()))
    for i in data["EndUseFuels"]:
        fuel_list = data["EndUseFuels"][i]
        for grid_region in grid_regions:
            fuel_list.append(f"ELC{grid_region}02")
        data["EndUseFuels"][i] = fuel_list
    data["TransformationTechnologies"] = [
        [
            f"PWRTRN{grid_region}",
            f"ELC{grid_region}01",
            "1.11",
            f"ELC{grid_region}02",
            "1",
            "Power transmission",
            "1",
        ]
        for grid_region in grid_regions
    ]
'''


def fix(path: Path, check_only: bool = False) -> str:
    text = path.read_text(encoding="utf-8")
    if FIXED in text and BUGGY not in text:
        return "already fixed"
    if BUGGY not in text:
        raise ValueError(
            "The pinned CLEWs Global transmission block was not recognized; "
            "inspect the upstream revision before changing it."
        )
    if check_only:
        raise ValueError("The land-code transmission-generation defect is present.")
    path.write_text(text.replace(BUGGY, FIXED, 1), encoding="utf-8")
    return "fixed"


def self_test() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "clewsy.py"
        path.write_text("before\n" + BUGGY + "after\n", encoding="utf-8")
        assert fix(path) == "fixed"
        corrected = path.read_text(encoding="utf-8")
        assert BUGGY not in corrected
        assert FIXED in corrected
        assert "PWRTRN{grid_region}" in corrected
        assert "ELC{grid_region}01" in corrected
        assert "ELC{grid_region}02" in corrected
        assert fix(path, check_only=True) == "already fixed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("PASS: CLEWs grid-mapping correction self-test")
        return
    if args.path is None:
        parser.error("path is required unless --self-test is used")
    print(f"{args.path}: {fix(args.path, check_only=args.check)}")


if __name__ == "__main__":
    main()
