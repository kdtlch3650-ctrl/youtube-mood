import unittest

from app.ai.bedrock_client import load_request_hints


class BedrockClientTests(unittest.TestCase):
    def test_builds_local_request_hints_when_bedrock_is_disabled(self) -> None:
        hints = load_request_hints("우울해서 신나는 곡을 듣고 싶어")

        self.assertEqual(hints.emotion_text, "우울해서")
        self.assertIn("신나는 곡을", hints.request_text)
        self.assertIn("신나는 곡을", hints.request_keywords)
        self.assertIn("uplifting", hints.preferred_mood_tags)
        self.assertIn("light", hints.preferred_mood_tags)
        self.assertIn("soft", hints.preferred_mood_tags)
        self.assertIn("warm", hints.preferred_mood_tags)
        self.assertIn("heavy", hints.blocked_mood_tags)
        self.assertIn("late night", hints.blocked_mood_tags)
        self.assertIn("upbeat music", hints.extra_keywords)

    def test_splits_negative_request_phrase(self) -> None:
        hints = load_request_hints("편안한 기분이야 하지만 너무 지루한 곡은 듣고 싶지않아 댄스곡이였으면 좋겠어")

        self.assertEqual(hints.emotion_text, "편안한 기분이야 하지만 너무")
        self.assertEqual(hints.negative_text, "지루한 곡은 듣고 싶지않아")
        self.assertEqual(hints.request_text, "댄스곡이였으면 좋겠어")
        self.assertTrue(hints.has_negation)
        self.assertEqual(hints.search_scope_hint, None)

    def test_extracts_desire_request_phrase(self) -> None:
        hints = load_request_hints("오늘은 너무 지쳤어 신나는 댄스곡이였으면 좋겠어")

        self.assertEqual(hints.request_text, "신나는 댄스곡이였으면 좋겠어")
        self.assertEqual(hints.negative_text, "")
        self.assertIn("신나는 댄스곡이였으면", hints.request_keywords[0])
        self.assertIn("uplifting", hints.preferred_mood_tags)
        self.assertIn("light", hints.preferred_mood_tags)


if __name__ == "__main__":
    unittest.main()
