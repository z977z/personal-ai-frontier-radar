import unittest

from src.collectors import parse_feed
from src.llm import MockProvider
from src.reporting import render_daily


class FeedAndReportTests(unittest.TestCase):
    def test_atom_parser(self):
        xml = b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>AI Agent</title><link href="https://example.com/a"/><updated>2026-08-31T00:00:00Z</updated><summary>Useful work</summary></entry></feed>'''
        items = parse_feed(xml, "Example", "official")
        self.assertEqual(items[0].title, "AI Agent")
        self.assertEqual(items[0].url, "https://example.com/a")

    def test_mock_structured_output_and_report(self):
        event = {"id": "1", "title": "MCP Agent", "summary": "Official update", "published_at": "2026", "sources": [{"name": "Official", "url": "https://example.com", "type": "official"}], "pre_score": 7.0}
        data = MockProvider().analyze([event]).data
        report = render_daily("2026-08-31", data["events"], data["concept"], data["build"], "mock", [])
        self.assertIn("https://example.com", report)
        self.assertIn("Facts", report)
        self.assertIn("AI Build", report)


if __name__ == "__main__":
    unittest.main()
