# M3U and M3U8 Playlist Format

M3U is a text-based playlist format. An extended M3U playlist commonly starts with the `#EXTM3U` header and uses `#EXTINF` records to describe media entries.

## Basic structure

A simple extended playlist can look like this:

```m3u
#EXTM3U
#EXTINF:-1,Example Channel
https://example.com/live/example.m3u8
```

In this example:

- `#EXTM3U` identifies the file as an extended M3U playlist.
- `#EXTINF` introduces metadata for the next media location.
- `-1` is a commonly used duration value for a live or unknown-length item.
- The text after the comma is the display name.
- The following line contains the media location.

## M3U versus M3U8

M3U8 is commonly used for UTF-8 encoded M3U playlist text. The file extension alone does not guarantee that every playlist uses the same set of tags or that every referenced stream is playable.

## Common structural problems

- Missing `#EXTM3U` header.
- An `#EXTINF` record with no following media location.
- A media location with no preceding `#EXTINF` metadata.
- An empty display name.
- Repeated media locations.

## What this project checks

M3U Playlist Inspector checks local playlist structure and reports the issues listed above. It does not make network requests, test whether a media location is online, validate stream playback, or determine whether content is licensed.

## Safe handling

Playlist files can contain private URLs, access tokens, or account-specific information. Keep real playlists private and use synthetic examples when sharing bug reports or documentation.

Only inspect playlists and media locations that you own or are authorized to use.
