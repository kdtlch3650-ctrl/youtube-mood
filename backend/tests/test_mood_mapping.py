import unittest

from app.ai.mood_mapping import adjust_mood_tags_by_text, build_mood_tags, build_search_keywords, resolve_mood_tags


class MoodMappingTests(unittest.TestCase):
    def test_builds_mood_tags_for_tiredness(self) -> None:
        self.assertEqual(build_mood_tags(["tiredness"]), ["soft", "quiet", "warm"])

    def test_adjusts_mood_tags_for_avoidance_phrase(self) -> None:
        tags = adjust_mood_tags_by_text(["heavy", "late night", "warm"], "불안하지만 너무 무거운 음악은 싫어")
        self.assertIn("soft", tags)
        self.assertIn("light", tags)
        self.assertNotIn("heavy", tags)
        self.assertNotIn("late night", tags)

    def test_builds_search_keywords_without_genre(self) -> None:
        keywords = build_search_keywords(["tiredness"], ["soft", "quiet"])
        self.assertEqual(keywords, ["soft emotional music", "quiet calm playlist", "tiredness mood music"])

    def test_builds_search_keywords_with_genre(self) -> None:
        keywords = build_search_keywords(["tiredness"], ["soft", "quiet"], "jazz")
        self.assertEqual(keywords, ["soft jazz music", "soft jazz playlist", "quiet calm jazz music"])

    def test_resolves_related_blocked_tags(self) -> None:
        tags = resolve_mood_tags(["soft", "quiet", "warm"], preferred_mood_tags=["uplifting"], blocked_mood_tags=["heavy"])
        self.assertNotIn("heavy", tags)
        self.assertNotIn("late night", tags)
        self.assertIn("uplifting", tags)


if __name__ == "__main__":
    unittest.main()
