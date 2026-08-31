import unittest

from src.notifications import render_email_html


class NotificationTests(unittest.TestCase):
    def test_email_escapes_untrusted_content(self):
        events = [{"title": "<script>alert(1)</script>", "analysis": "Useful & safe"}]
        result = render_email_html("2026-08-31", events, {"name_zh": "概念", "name_en": "Concept", "explanation": "Text"}, {"name_zh": "项目", "name_en": "Build", "tagline": "Demo"}, "https://example.com")
        self.assertNotIn("<script>", result)
        self.assertIn("&lt;script&gt;", result)
        self.assertIn("Read Full Report", result)


if __name__ == "__main__":
    unittest.main()
