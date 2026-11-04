# Usage Guide

This guide explains how to run M3U Playlist Inspector with a local playlist file.

## Inspect a playlist

From the repository directory:

```bash
python3 m3u_inspector.py examples/sample.m3u
```

## Show parsed entries

```bash
python3 m3u_inspector.py examples/sample.m3u --show-entries
```

## Export reports

```bash
python3 m3u_inspector.py examples/sample.m3u --json report.json --csv report.csv
```

The JSON file contains the source filename, header status, entry and issue counts, parsed entries, and issue details. The CSV file contains one row per issue.

## Validation checks

The inspector checks the extended M3U header, missing media locations, URLs without preceding metadata, empty display names, duplicate locations, and basic EXTINF syntax. EXTINF durations must be finite numbers; decimal durations and the commonly used `-1` value are accepted.

## Exit codes

- `0`: no structural errors were found.
- `1`: one or more structural errors were found.
- `2`: the input could not be read or an output report could not be written.

Warnings do not currently cause a non-zero exit code.

## Important limitations

The current version performs local structural checks. It does not connect to URLs, test stream availability, resolve DNS, play media, or verify content rights. Some advanced HLS playlist constructs may need dedicated parsing support in a future release.
