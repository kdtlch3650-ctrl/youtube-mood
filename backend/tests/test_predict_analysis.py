import unittest
from unittest.mock import patch

from app.ai.bedrock_client import RequestHints
from app.ai.predict import predict_analysis


class FakeModel:
    def predict(self, text: str) -> dict[str, list[str]]:
        return {
            "emotions": ["tiredness"],
            "mood_tags": [],
        }


class PredictAnalysisTests(unittest.TestCase):
    @patch(
        "app.ai.predict.load_request_hints",
        return_value=RequestHints(
            emotion_text="오늘은 너무 지쳐",
            request_text="신나는 곡을 듣고 싶어",
            request_keywords=["신나는 곡을"],
            preferred_mood_tags=["uplifting", "light"],
            avoid_mood_tags=[],
            extra_keywords=["upbeat music"],
            has_avoidance=True,
            has_negation=True,
        ),
    )
    @patch("app.ai.predict.load_model", return_value=FakeModel())
    def test_predict_analysis_uses_emotion_text_and_request_keywords(self, mocked_load_model, mocked_load_request_hints) -> None:
        result = predict_analysis("오늘은 너무 지쳐서 신나는 곡을 듣고 싶어")

        self.assertEqual(result.input_text, "오늘은 너무 지쳐서 신나는 곡을 듣고 싶어")
        self.assertEqual(result.emotion_text, "오늘은 너무 지쳐")
        self.assertEqual(result.request_text, "신나는 곡을 듣고 싶어")
        self.assertEqual(result.genre, None)
        self.assertEqual(result.emotions, ["tiredness"])
        self.assertEqual(result.mood_tags, ["uplifting", "light", "soft", "quiet"])
        self.assertEqual(result.search_keywords, ["신나는 곡을", "upbeat music", "uplifting mood music"])
        self.assertTrue(result.has_avoidance)
        self.assertTrue(result.has_negation)
        self.assertEqual(result.request_keywords, ["신나는 곡을"])

        mocked_load_model.assert_called_once()
        mocked_load_request_hints.assert_called_once()


if __name__ == "__main__":
    unittest.main()
