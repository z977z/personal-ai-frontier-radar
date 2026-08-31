import unittest

from src.models import SourceItem
from src.processing import deduplicate, pre_score


class ProcessingTests(unittest.TestCase):
    def item(self, title, url):
        return SourceItem(title, url, "Official", "2026-08-31", "2026-08-31", "Agent model release", source_type="official")

    def test_exact_url_dedup(self):
        events = deduplicate([self.item("New Agent Model", "https://x.test/a"), self.item("Other title", "https://x.test/a")])
        self.assertEqual(len(events), 1)

    def test_similar_title_clusters_sources(self):
        events = deduplicate([self.item("Company releases new agent model", "https://a.test/1"), self.item("Company releases a new agent model", "https://b.test/2")])
        self.assertEqual(len(events), 1)
        self.assertEqual(len(events[0].sources), 2)

    def test_pre_score_is_bounded(self):
        event = deduplicate([self.item("Agent model release benchmark MCP reasoning", "https://x.test/a")])[0]
        self.assertTrue(0 <= pre_score(event) <= 10)


if __name__ == "__main__":
    unittest.main()

