import unittest

from m3u_inspector import parse_playlist


class PlaylistParserTests(unittest.TestCase):
    def test_valid_playlist(self):
        entries, issues, valid = parse_playlist(
            "#EXTM3U\n#EXTINF:-1,News\nhttps://example.test/news.m3u8\n"
        )
        self.assertTrue(valid)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "News")
        self.assertEqual(issues, [])

    def test_missing_header(self):
        _, issues, valid = parse_playlist("#EXTINF:-1,News\nhttps://example.test/a")
        self.assertFalse(valid)
        self.assertIn("missing_header", [item.code for item in issues])

    def test_missing_url(self):
        _, issues, _ = parse_playlist("#EXTM3U\n#EXTINF:-1,News\n")
        self.assertIn("missing_url", [item.code for item in issues])

    def test_duplicate_url(self):
        text = ("#EXTM3U\n#EXTINF:-1,A\nhttps://example.test/a\n"
                "#EXTINF:-1,B\nhttps://example.test/a\n")
        _, issues, _ = parse_playlist(text)
        self.assertIn("duplicate_url", [item.code for item in issues])

    def test_empty_name(self):
        _, issues, _ = parse_playlist("#EXTM3U\n#EXTINF:-1,\nhttps://example.test/a")
        self.assertIn("empty_name", [item.code for item in issues])


if __name__ == "__main__":
    unittest.main()
