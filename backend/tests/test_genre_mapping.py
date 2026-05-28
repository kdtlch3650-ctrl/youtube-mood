import unittest

from app.ai.genre_mapping import extract_genre


class GenreMappingTests(unittest.TestCase):
    def test_extracts_safe_genre(self) -> None:
        self.assertEqual(extract_genre("오늘은 지쳤는데 차분한 재즈 음악 듣고 싶어"), "jazz")

    def test_extracts_ambiguous_genre_with_music_context(self) -> None:
        self.assertEqual(extract_genre("하우스 음악으로 신나는 곡 추천해줘"), "house")

    def test_ignores_ambiguous_genre_without_music_context(self) -> None:
        self.assertIsNone(extract_genre("집에서 쉬고 싶은데 편안한 음악 추천해줘"))

    def test_ignores_negative_recommendation_context(self) -> None:
        self.assertIsNone(extract_genre("trap이라는 말은 봤지만 음악 추천은 아니야"))

    def test_prefers_first_matching_genre(self) -> None:
        self.assertEqual(extract_genre("재즈와 로파이 중에 뭘 들을까"), "jazz")


if __name__ == "__main__":
    unittest.main()
