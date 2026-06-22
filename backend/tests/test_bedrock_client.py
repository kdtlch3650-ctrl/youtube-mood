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
        self.assertIn("upbeat music", hints.extra_keywords)


if __name__ == "__main__":
    unittest.main()
