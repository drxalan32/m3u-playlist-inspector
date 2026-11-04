# M3U Playlist Inspector

A privacy-friendly command-line tool for checking local M3U and M3U8 playlist structure. Use it only with playlists you own or are authorized to inspect.

## Features
- Check the #EXTM3U header and EXTINF/media URL structure.
- Detect missing metadata, empty channel names, and duplicate URLs.
- Export JSON and CSV reports.
- Process files locally: no uploads and no network requests.

## Requirements
Python 3.9+. No third-party dependencies.

## Quick start
```bash
git clone https://github.com/drxalan32/m3u-playlist-inspector.git
cd m3u-playlist-inspector
python3 m3u_inspector.py path/to/playlist.m3u
```

Export reports:
```bash
python3 m3u_inspector.py path/to/playlist.m3u --json report.json --csv report.csv
```

Show parsed channel names:
```bash
python3 m3u_inspector.py path/to/playlist.m3u --show-entries
```

Run tests:
```bash
python3 -m unittest discover -s tests -v
```

## Scope and limitations
This is a structural validator only. It does not test stream availability, play media, provide channel lists, or determine licensing status.

## Responsible use
Only inspect playlists and media URLs you own or are authorized to use. Do not publish private playlists, credentials, or stream URLs in issues or pull requests.

## License
MIT. See [LICENSE](LICENSE).
