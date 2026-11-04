import unittest

from m3u_inspector import parse_playlist


class PlaylistParserTests(unittest.TestCase):
    def test_valid_playlist(self):
        entries, issues, valid = parse_playlist(
            "#EXTM3U\\n#EXTINF:-1,News\\nhttps://example.test/news.m3u8\\n"
        )
        self.assertTrue(valid)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].name, "News")
        self.assertEqual(issues, [])

    def test_missing_header(self):
        _, issues, valid = parse_playlist("#EXTINF:-1,News\\nhttps://example.test/a")
        self.assertFalse(valid)
        self.assertIn("missing_header", [item.code for item in issues])

    def test_missing_url(self):
        _, issues, _ = parse_playlist("#EXTM3U\\n#EXTINF:-1,News\\n")
        self.assertIn("missing_url", [item.code for item in issues])

    def test_duplicate_url(self):
        text = ("#EXTM3U\\n#EXTINF:-1,A\\nhttps://example.test/a\\n"
                "#EXTINF:-1,B\\nhttps://example.test/a\\n")
        _, issues, _ = parse_playlist(text)
        self.assertIn("duplicate_url", [item.code for item in issues])

    def test_empty_name(self):
        _, issues, _ = parse_playlist("#EXTM3U\\n#EXTINF:-1,\\nhttps://example.test/a")
        self.assertIn("empty_name", [item.code for item in issues])

    def test_url_without_extinf(self):
        entries, issues, _ = parse_playlist("#EXTM3U\\nhttps://example.test/a\\n")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].url, "https://example.test/a")
        self.assertIn("url_without_extinf", [item.code for item in issues])

    def test_empty_playlist(self):
        entries, issues, valid = parse_playlist("#EXTM3U\\n\\n")
        self.assertTrue(valid)
        self.assertEqual(entries, [])
        self.assertIn("empty_playlist", [item.code for item in issues])

    def test_second_extinf_reports_previous_missing_url(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\\n#EXTINF:-1,First\\n#EXTINF:-1,Second\\nhttps://example.test/b\\n"
        )
        missing = [item for item in issues if item.code == "missing_url"]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].line, 2)

    def test_duplicate_warning_points_to_second_entry(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\\n#EXTINF:-1,A\\nhttps://example.test/a\\n"
            "#EXTINF:-1,B\\nhttps://example.test/a\\n"
        )
        duplicate = next(item for item in issues if item.code == "duplicate_url")
        self.assertEqual(duplicate.line, 4)

    def test_lowercase_extinf_is_accepted(self):
        entries, issues, _ = parse_playlist(
            "#EXTM3U\\n#extinf:-1,News\\nhttps://example.test/news.m3u8\\n"
        )
        self.assertEqual(entries[0].name, "News")
        self.assertEqual(issues, [])

    def test_decimal_duration_is_accepted(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\\n#EXTINF:12.5,Clip\\nhttps://example.test/clip.mp4\\n"
        )
        self.assertNotIn("invalid_extinf", [item.code for item in issues])

    def test_extinf_missing_comma_is_reported(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\\n#EXTINF:-1 News\\nhttps://example.test/news.m3u8\\n"
        )
        self.assertIn("invalid_extinf", [item.code for item in issues])

    def test_extinf_invalid_duration_is_reported(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\\n#EXTINF:live,News\\nhttps://example.test/news.m3u8\\n"
        )
        self.assertIn("invalid_extinf", [item.code for item in issues])

    def test_extinf_non_finite_duration_is_reported(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\\n#EXTINF:NaN,News\\nhttps://example.test/news.m3u8\\n"
        )
        self.assertIn("invalid_extinf", [item.code for item in issues])


if __name__ == "__main__":
    unittest.main()
