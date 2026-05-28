from pathlib import Path
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
TEST_CASE_DOC = PROJECT_DIR / "docs" / "14-recommendation-test-cases.md"

sys.path.insert(0, str(BACKEND_DIR))

from app.ai.predict import predict_analysis  # noqa: E402
from app.youtube import KOREAN_GENRE_NAMES, build_youtube_query  # noqa: E402


def normalize_cell(value: str) -> str:
    return value.strip().strip("`")


def parse_test_cases() -> list[dict[str, str | None]]:
    rows = []
    text = TEST_CASE_DOC.read_text(encoding="utf-8")

    for line in text.splitlines():
        if not line.startswith("| T"):
            continue

        cells = [normalize_cell(cell) for cell in line.strip("|").split("|")]
        if len(cells) != 5:
            continue

        case_id, input_text, scope_label, expected_genre, expected_direction = cells
        rows.append(
            {
                "case_id": case_id,
                "input_text": input_text,
                "search_scope": "korean" if " " in scope_label else "all",
                "expected_genre": expected_genre if expected_genre.isascii() else None,
                "expected_direction": expected_direction,
            }
        )

    return rows


def includes_expected_genre(query: str, expected_genre: str | None, search_scope: str) -> bool:
    if expected_genre is None:
        return True

    expected_query_part = expected_genre
    if search_scope == "korean":
        expected_query_part = KOREAN_GENRE_NAMES.get(expected_genre, expected_genre)

    return expected_query_part.lower() in query.lower()


def run() -> int:
    cases = parse_test_cases()
    check_cases = []

    for case in cases:
        result = predict_analysis(str(case["input_text"]))
        query = build_youtube_query(
            result.search_keywords,
            result.mood_tags,
            result.genre,
            case["search_scope"],  # type: ignore[arg-type]
            "music",
        )

        expected_genre = case["expected_genre"]
        genre_ok = result.genre == expected_genre
        query_ok = includes_expected_genre(query, expected_genre, str(case["search_scope"]))
        status = "PASS" if genre_ok and query_ok else "CHECK"

        if status != "PASS":
            check_cases.append(str(case["case_id"]))

        print(f"{case['case_id']} {status}")
        print(f"  input: {case['input_text']}")
        print(f"  expected_genre: {expected_genre}")
        print(f"  actual_genre: {result.genre}")
        print(f"  mood_tags: {result.mood_tags}")
        print(f"  query: {query}")

    print(f"TOTAL: {len(cases)}")
    print(f"PASS: {len(cases) - len(check_cases)}")
    print(f"CHECK: {len(check_cases)}")

    if check_cases:
        print(f"CHECK_CASES: {', '.join(check_cases)}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
