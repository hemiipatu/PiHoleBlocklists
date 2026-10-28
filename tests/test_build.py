import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build


class ExtractDomainsTests(unittest.TestCase):
    def test_extracts_hosts_file_aliases_and_ignores_inline_comment(self):
        self.assertEqual(
            build.extract_domains("0.0.0.0 first.example second.example # comment"),
            {"first.example", "second.example"},
        )

    def test_extracts_adblock_rule(self):
        self.assertEqual(
            build.extract_domains("||ads.example^$third-party"),
            {"ads.example"},
        )

    def test_ignores_comments_and_invalid_entries(self):
        self.assertEqual(build.extract_domains("# comment"), set())
        self.assertEqual(build.extract_domains("0.0.0.0 localhost"), set())
        self.assertEqual(build.extract_domains("||*.example^"), set())


class FetchDomainsTests(unittest.TestCase):
    def test_source_failure_aborts_build(self):
        with (
            patch("build.urllib.request.urlopen", side_effect=OSError("offline")),
            self.assertRaisesRegex(RuntimeError, "Failed to fetch source"),
        ):
            build.fetch_domains_from_urls(["https://example.test/list"], set())


class WriteTierFileTests(unittest.TestCase):
    def test_unchanged_domains_preserve_existing_file(self):
        with tempfile.TemporaryDirectory() as output_dir:
            output_path = Path(output_dir) / "basic.txt"
            original_content = "# Previous version\n0.0.0.0 ads.example\n"
            output_path.write_text(original_content, encoding="utf-8")

            with patch.object(build, "OUTPUT_DIR", output_dir):
                build.write_tier_file("basic.txt", {"ads.example"}, "Basic")

            self.assertEqual(output_path.read_text(encoding="utf-8"), original_content)


if __name__ == "__main__":
    unittest.main()