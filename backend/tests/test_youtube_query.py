import unittest

from app.youtube import build_youtube_query


class YoutubeQueryTests(unittest.TestCase):
    def test_builds_all_scope_query(self) -> None:
        query = build_youtube_query(["warm comfort dance music"], ["warm", "soft"], "dance", "all", "music")
        self.assertEqual(query, "warm comfort dance music")

    def test_builds_korean_scope_music_query(self) -> None:
        query = build_youtube_query(["warm comfort dance music"], ["warm", "soft"], "dance", "korean", "music")
        self.assertEqual(query, "따뜻한 댄스 음악")

    def test_builds_korean_scope_playlist_query(self) -> None:
        query = build_youtube_query(["warm comfort dance music"], ["warm", "soft"], "dance", "korean", "playlist")
        self.assertEqual(query, "따뜻한 댄스 플레이리스트")


if __name__ == "__main__":
    unittest.main()
