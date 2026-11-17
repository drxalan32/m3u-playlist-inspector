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

    def test_url_without_extinf(self):
        entries, issues, _ = parse_playlist("#EXTM3U\nhttps://example.test/a\n")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].url, "https://example.test/a")
        self.assertIn("url_without_extinf", [item.code for item in issues])

    def test_empty_playlist(self):
        entries, issues, valid = parse_playlist("#EXTM3U\n\n")
        self.assertTrue(valid)
        self.assertEqual(entries, [])
        self.assertIn("empty_playlist", [item.code for item in issues])

    def test_second_extinf_reports_previous_missing_url(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:-1,First\n#EXTINF:-1,Second\nhttps://example.test/b\n"
        )
        missing = [item for item in issues if item.code == "missing_url"]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].line, 2)

    def test_duplicate_warning_points_to_second_entry(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:-1,A\nhttps://example.test/a\n"
            "#EXTINF:-1,B\nhttps://example.test/a\n"
        )
        duplicate = next(item for item in issues if item.code == "duplicate_url")
        self.assertEqual(duplicate.line, 4)

    def test_lowercase_extinf_is_accepted(self):
        entries, issues, _ = parse_playlist(
            "#EXTM3U\n#extinf:-1,News\nhttps://example.test/news.m3u8\n"
        )
        self.assertEqual(entries[0].name, "News")
        self.assertEqual(issues, [])

    def test_decimal_duration_is_accepted(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:12.5,Clip\nhttps://example.test/clip.mp4\n"
        )
        self.assertNotIn("invalid_extinf", [item.code for item in issues])

    def test_extinf_missing_comma_is_reported(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:-1 News\nhttps://example.test/news.m3u8\n"
        )
        self.assertIn("invalid_extinf", [item.code for item in issues])

    def test_extinf_invalid_duration_is_reported(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:live,News\nhttps://example.test/news.m3u8\n"
        )
        self.assertIn("invalid_extinf", [item.code for item in issues])

    def test_extinf_non_finite_duration_is_reported(self):
        _, issues, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:NaN,News\nhttps://example.test/news.m3u8\n"
        )
        self.assertIn("invalid_extinf", [item.code for item in issues])

    def test_header_with_attributes_is_valid(self):
        entries, issues, valid = parse_playlist(
            '#EXTM3U x-tvg-url="https://example.test/guide.xml"\n'
            "#EXTINF:-1,News\nhttps://example.test/news.m3u8\n"
        )
        self.assertTrue(valid)
        self.assertNotIn("missing_header", [item.code for item in issues])
        self.assertEqual(len(entries), 1)

    def test_header_prefix_without_separator_is_not_a_header(self):
        _, issues, valid = parse_playlist("#EXTM3UX\n#EXTINF:-1,News\nhttps://example.test/a\n")
        self.assertFalse(valid)
        self.assertIn("missing_header", [item.code for item in issues])

    def test_comma_inside_attribute_value_does_not_split_name(self):
        entries, issues, _ = parse_playlist(
            '#EXTM3U\n#EXTINF:-1 tvg-id="a" group-title="News, Sports",BBC One\n'
            "https://example.test/a\n"
        )
        self.assertEqual(entries[0].name, "BBC One")
        self.assertEqual(issues, [])

    def test_comma_only_inside_quotes_is_reported_as_missing_separator(self):
        _, issues, _ = parse_playlist(
            '#EXTM3U\n#EXTINF:-1 group-title="News, Sports"\nhttps://example.test/a\n'
        )
        self.assertIn("invalid_extinf", [item.code for item in issues])

    def test_name_keeps_commas_after_the_separator(self):
        entries, _, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:-1,Hello, World\nhttps://example.test/a\n"
        )
        self.assertEqual(entries[0].name, "Hello, World")

    def test_crlf_and_lone_cr_line_endings(self):
        for newline in ("\r\n", "\r"):
            with self.subTest(newline=repr(newline)):
                text = newline.join(
                    ["#EXTM3U", "#EXTINF:-1,A", "https://example.test/a", "#EXTINF:-1,B",
                     "https://example.test/b", ""]
                )
                entries, issues, _ = parse_playlist(text)
                self.assertEqual([e.name for e in entries], ["A", "B"])
                self.assertEqual([e.line for e in entries], [2, 4])
                self.assertEqual(issues, [])

    def test_unicode_line_separators_do_not_split_lines(self):
        entries, issues, _ = parse_playlist(
            "#EXTM3U\n#EXTINF:-1,Foo\N{LINE SEPARATOR}Bar\nhttps://example.test/a\n"
            "#EXTINF:-1,Baz\x85Qux\nhttps://example.test/b\n"
        )
        self.assertEqual(len(entries), 2)
        self.assertEqual([e.line for e in entries], [2, 4])
        self.assertEqual(issues, [])

    def test_duration_grammar_matches_browser_tools(self):
        for duration in ("1_0", "\N{ARABIC-INDIC DIGIT ONE}\N{ARABIC-INDIC DIGIT TWO}", "--1", "1e", "0x10"):
            with self.subTest(duration=duration):
                _, issues, _ = parse_playlist(
                    f"#EXTM3U\n#EXTINF:{duration},X\nhttps://example.test/a\n"
                )
                self.assertIn("invalid_extinf", [item.code for item in issues])
        for duration in ("-1", "0", "12.5", "+3", ".5", "1e3", "5."):
            with self.subTest(duration=duration):
                _, issues, _ = parse_playlist(
                    f"#EXTM3U\n#EXTINF:{duration},X\nhttps://example.test/a\n"
                )
                self.assertEqual(issues, [])

    def test_overflowing_duration_is_not_finite(self):
        _, issues, _ = parse_playlist("#EXTM3U\n#EXTINF:1e999,X\nhttps://example.test/a\n")
        self.assertIn("invalid_extinf", [item.code for item in issues])


if __name__ == "__main__":
    unittest.main()
