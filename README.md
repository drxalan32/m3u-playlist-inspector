# M3U Playlist Inspector – M3U and M3U8 Playlist Validator

[![Tests](https://github.com/drxalan32/m3u-playlist-inspector/actions/workflows/tests.yml/badge.svg)](https://github.com/drxalan32/m3u-playlist-inspector/actions/workflows/tests.yml)

**M3U Playlist Inspector** is a free, open-source Python command-line tool for validating local **M3U and M3U8 playlist files**. Check playlist structure, find missing channel metadata, identify duplicate stream URLs, and export JSON or CSV reports — all directly on your computer.

It is designed for developers, playlist maintainers, and users who need a simple **M3U playlist checker** without uploading playlist contents to an online service.

> **Privacy first:** playlist files are read locally. The tool does not connect to stream URLs or send playlist data to a server.

## Key features

- **M3U and M3U8 validation:** check the #EXTM3U header and #EXTINF entry structure.
- **Missing metadata detection:** find entries with missing media URLs or channel names.
- **Duplicate URL detection:** identify repeated media URLs in a playlist.
- **Playlist issue reports:** display errors and warnings with source line numbers.
- **JSON export:** save structured results for scripts and other tools.
- **CSV export:** open issue reports in spreadsheet software.
- **Local processing:** inspect files without uploading them or making network requests.
- **Zero dependencies:** built with the Python standard library.

## Quick start

### Requirements

- Python 3.9 or newer
- Git (for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/drxalan32/m3u-playlist-inspector.git
cd m3u-playlist-inspector
```

### 2. Run the M3U validator

Pass the path to a playlist file you are authorized to inspect:

```bash
python3 m3u_inspector.py path/to/playlist.m3u
```

The tool prints the number of entries, errors, warnings, duplicate URLs, and the line number for each detected issue.

### 3. Export JSON and CSV reports

```bash
python3 m3u_inspector.py path/to/playlist.m3u --json report.json --csv report.csv
```

### 4. Display parsed channel names

```bash
python3 m3u_inspector.py path/to/playlist.m3u --show-entries
```

### 5. Run the test suite

```bash
python3 -m unittest discover -s tests -v
```

## Try the online M3U tools

No installation is needed to try the browser-based tools:

- **[Online M3U Playlist Checker](https://drxalan32.github.io/m3u-playlist-inspector/)** — inspect a local M3U or M3U8 file in your browser.
- **[M3U Playlist Generator](https://drxalan32.github.io/m3u-playlist-inspector/#playlist-generator)** — create, import, edit, reorder, and export a playlist.
- **[How to validate an M3U playlist](https://drxalan32.github.io/m3u-playlist-inspector/how-to-validate-m3u-playlist.html)** — step-by-step guide.
- **[M3U vs M3U8](https://drxalan32.github.io/m3u-playlist-inspector/m3u-vs-m3u8.html)** — understand the formats.
- **[M3U file format guide](https://drxalan32.github.io/m3u-playlist-inspector/m3u-file-format.html)** — learn the playlist structure.
- **[IPTV M3U Playlist Guide](https://drxalan32.github.io/m3u-playlist-inspector/iptv-m3u-playlist-guide.html)** — understand channel metadata, EPG identifiers and safe playlist validation.
- **[How to organize an M3U playlist](https://drxalan32.github.io/m3u-playlist-inspector/m3u-playlist-organization.html)** — organize channel names, groups and metadata consistently.

The online tools process selected playlist text in your browser. They do not test network stream availability or guarantee playback.

## Documentation

- [Usage guide](docs/usage.md): commands, report formats, and exit codes.
- [M3U and M3U8 format reference](docs/m3u-format.md): playlist structure and common formatting problems.
- [Contributing guidelines](CONTRIBUTING.md): how to report issues and contribute safely.
- [Security and privacy policy](SECURITY.md): how to report security concerns and protect private playlist data.

## What does the M3U playlist checker validate?

| Check | Result |
| --- | --- |
| Missing or invalid #EXTM3U header | Error |
| #EXTINF entry without a media URL | Error |
| Media URL without preceding #EXTINF metadata | Warning |
| Empty channel display name | Warning |
| Duplicate media URL | Warning |
| Playlist with no media entries | Warning |

The inspector focuses on playlist structure and common formatting problems. It does not determine whether a stream is online, playable, safe, or legally licensed.

## Example command output

```text
M3U Playlist Inspector
File: playlist.m3u
Entries: 12
Errors: 1
Warnings: 2
Duplicate URLs: 1
```

Your results will depend on the contents of the local playlist file.

## Common questions

### What is an M3U playlist?

M3U is a plain-text playlist format that can contain media locations and optional metadata. M3U8 is a UTF-8-based variant commonly used for playlists and streaming media references.

### Can I use this tool to check an M3U8 file?

Yes. The inspector reads local UTF-8 text files, including M3U and M3U8 playlists. Provide the file path as the command-line argument.

### Does the tool check whether IPTV streams are working?

No. It checks playlist formatting and metadata only. It does not request, probe, or play stream URLs.

### Does the inspector upload my playlist?

No. Playlist inspection is performed locally. The program does not send playlist contents to an external service.

### Do I need to install Python packages?

No additional packages are required. The project uses Python's standard library.

## Responsible use

Use M3U Playlist Inspector only with playlist files and media URLs that you own or are authorized to inspect. You are responsible for respecting copyright, service terms, privacy, and applicable laws.

Do not publish private playlist files, credentials, subscription details, or private stream URLs in GitHub issues, pull requests, or public examples.

## Contributing

Contributions, bug reports, and suggestions are welcome. Before opening an issue, remove private URLs, credentials, and personal information from logs and examples.

## License

This project is distributed under the [MIT License](LICENSE).
