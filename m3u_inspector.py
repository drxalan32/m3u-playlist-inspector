#!/usr/bin/env python3
"""Inspect a local M3U/M3U8 playlist without network access."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

# Same grammar as the browser tools: optional sign, digits, optional fraction/exponent.
# ASCII-only so values such as "1_0" or Arabic-Indic digits are not silently accepted.
_DURATION_RE = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", re.ASCII)
_HEADER_RE = re.compile(r"#EXTM3U(?:\s|$)", re.IGNORECASE)


@dataclass
class Issue:
    severity: str
    line: int
    code: str
    message: str


@dataclass
class Entry:
    line: int
    name: str
    info: str
    url: str


def _split_extinf(value: str) -> tuple[str, str | None]:
    """Split ``#EXTINF:<metadata>,<name>`` at the first comma outside double quotes.

    Attribute values may legitimately contain commas (``group-title="News, Sports"``),
    so a plain ``split(",")`` would cut the record in the wrong place.
    Returns ``(metadata, None)`` when there is no separating comma.
    """
    in_quotes = False
    for index, char in enumerate(value):
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            return value[:index], value[index + 1:]
    return value, None


def _extinf_problem(value: str) -> str | None:
    """Return a validation message when an EXTINF record is malformed."""
    metadata, name = _split_extinf(value)
    if name is None:
        return "EXTINF record is missing the comma that separates metadata from the display name."

    duration_and_attributes = metadata.split(":", 1)[1].strip()
    duration = duration_and_attributes.split(None, 1)[0] if duration_and_attributes else ""
    if not _DURATION_RE.fullmatch(duration):
        return "EXTINF duration must be a valid number."
    if not math.isfinite(float(duration)):
        return "EXTINF duration must be a finite number."
    return None


def parse_playlist(text: str) -> tuple[list[Entry], list[Issue], bool]:
    # str.splitlines() also breaks on U+2028, NEL, form feed, etc., which would shift line
    # numbers relative to the browser tools. Only CR, LF and CRLF end a playlist line.
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    issues: list[Issue] = []
    entries: list[Entry] = []
    first = next(((i, s.strip()) for i, s in enumerate(lines, 1) if s.strip()), None)
    # "#EXTM3U" may carry attributes, e.g. #EXTM3U x-tvg-url="https://example.test/epg.xml"
    header_valid = bool(first and _HEADER_RE.match(first[1]))
    if not header_valid:
        issues.append(Issue("ERROR", first[0] if first else 1, "missing_header",
                            "Playlist must start with an #EXTM3U header."))

    pending_info = None
    pending_line = 0
    for number, raw in enumerate(lines, 1):
        value = raw.strip()
        if not value or _HEADER_RE.match(value):
            continue
        if value.upper().startswith("#EXTINF:"):
            if pending_info is not None:
                issues.append(Issue("ERROR", pending_line, "missing_url",
                                    "EXTINF entry is missing its media URL before the next EXTINF."))
            problem = _extinf_problem(value)
            if problem:
                issues.append(Issue("WARNING", number, "invalid_extinf", problem))
            pending_info, pending_line = value, number
        elif value.startswith("#"):
            continue
        elif pending_info is None:
            issues.append(Issue("WARNING", number, "url_without_extinf",
                                "Media URL has no preceding EXTINF metadata."))
            entries.append(Entry(number, "", "", value))
        else:
            _, raw_name = _split_extinf(pending_info)
            has_name_separator = raw_name is not None
            name = raw_name.strip() if raw_name is not None else ""
            if has_name_separator and not name:
                issues.append(Issue("WARNING", pending_line, "empty_name",
                                    "EXTINF metadata has no channel display name."))
            entries.append(Entry(pending_line, name, pending_info, value))
            pending_info, pending_line = None, 0

    if pending_info is not None:
        issues.append(Issue("ERROR", pending_line, "missing_url",
                            "EXTINF entry is missing its media URL."))
    if not entries:
        issues.append(Issue("WARNING", 1, "empty_playlist", "No media entries were found."))

    seen: dict[str, int] = {}
    for entry in entries:
        if entry.url in seen:
            issues.append(Issue("WARNING", entry.line, "duplicate_url",
                                f"Duplicate media URL (first seen on line {seen[entry.url]})."))
        else:
            seen[entry.url] = entry.line
    return entries, issues, header_valid


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a local M3U/M3U8 playlist.")
    parser.add_argument("playlist", type=Path, help="Local .m3u or .m3u8 file")
    parser.add_argument("--json", dest="json_path", type=Path, help="Write a JSON report")
    parser.add_argument("--csv", dest="csv_path", type=Path, help="Write an issues CSV report")
    parser.add_argument("--show-entries", action="store_true", help="Show parsed entry names")
    args = parser.parse_args()

    try:
        source = args.playlist.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        print(f"Could not read playlist: {exc}", file=sys.stderr)
        return 2

    entries, issues, header_valid = parse_playlist(source)
    errors = sum(item.severity == "ERROR" for item in issues)
    warnings = sum(item.severity == "WARNING" for item in issues)
    duplicates = sum(item.code == "duplicate_url" for item in issues)

    print("M3U Playlist Inspector")
    print(f"File: {args.playlist}")
    print(f"Entries: {len(entries)}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
    print(f"Duplicate URLs: {duplicates}")
    for item in issues:
        print(f"{item.severity:<7} Line {item.line}: {item.message}")

    if args.show_entries:
        print("\nParsed entries:")
        for entry in entries:
            print(f"Line {entry.line}: {entry.name or '(unnamed)'}")

    try:
        if args.json_path:
            report = {
                "source": args.playlist.name,
                "header_valid": header_valid,
                "entry_count": len(entries),
                "error_count": errors,
                "warning_count": warnings,
                "entries": [asdict(item) for item in entries],
                "issues": [asdict(item) for item in issues],
            }
            args.json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                      encoding="utf-8")
            print(f"JSON report written to: {args.json_path}")
        if args.csv_path:
            with args.csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["severity", "line", "code", "message"])
                writer.writeheader()
                writer.writerows(asdict(item) for item in issues)
            print(f"CSV report written to: {args.csv_path}")
    except OSError as exc:
        print(f"Could not write report: {exc}", file=sys.stderr)
        return 2
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
