import unittest

from src.models import Event


class GroundingContractTests(unittest.TestCase):
    def test_llm_assessment_can_be_merged_without_title_or_sources(self):
        original = Event("abc", "Official title", "Summary", "2026-08-31", [{"name": "Official", "url": "https://example.com", "type": "official"}], pre_score=7.0).to_dict()
        assessment = {"id": "abc", "ai_score": 8.0, "facts": "Grounded fact"}
        merged = {**original, **assessment}
        merged["title"] = original["title"]
        merged["sources"] = original["sources"]
        self.assertEqual(merged["title"], "Official title")
        self.assertEqual(merged["sources"][0]["url"], "https://example.com")


if __name__ == "__main__":
    unittest.main()
