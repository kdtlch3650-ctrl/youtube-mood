import unittest
from unittest.mock import patch

from app.ai.predict import predict_analysis


class FakeModel:
    def predict(self, text: str) -> dict[str, list[str]]:
        return {
            "emotions": ["tiredness"],
            "mood_tags": [],
        }


class PredictAnalysisTests(unittest.TestCase):
    @patch("app.ai.predict.load_model", return_value=FakeModel())
    def test_predict_analysis_builds_genre_and_keywords(self, mocked_load_model) -> None:
        result = predict_analysis("오늘은 특히 너무 지쳐 신나는 댄스음악 추천해줘")

        self.assertEqual(result.genre, "dance")
        self.assertEqual(result.emotions, ["tiredness"])
        self.assertEqual(result.mood_tags, ["soft", "quiet", "warm"])
        self.assertEqual(result.search_keywords, ["soft dance music", "soft dance playlist", "quiet calm dance music"])

        mocked_load_model.assert_called_once()


if __name__ == "__main__":
    unittest.main()
