import sys
from pathlib import Path

BASE = Path(__file__).parent

# Search in clean (no diacritics) file; display from the original (with diacritics)
CLEAN_FILE = BASE.parent / "quran-simple-clean.txt"
DISPLAY_FILE = BASE / "quran-simple.txt"


def parse_file(path: Path) -> dict[tuple[int, int], str]:
    """Return {(surah, ayah): text} for every verse in the file."""
    verses = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("|", 2)
            if len(parts) != 3:
                continue
            surah, ayah, text = int(parts[0]), int(parts[1]), parts[2]
            verses[(surah, ayah)] = text
    return verses


def search(word: str) -> tuple[int, list[tuple[int, int, str]]]:
    """
    Search `word` in the clean file.
    Return (total_occurrences, [(surah, ayah, display_text), ...]).
    """
    clean_verses = parse_file(CLEAN_FILE)
    display_verses = parse_file(DISPLAY_FILE)

    total = 0
    results = []

    for (surah, ayah), clean_text in clean_verses.items():
        count = clean_text.count(word)
        if count:
            total += count
            display_text = display_verses.get((surah, ayah), clean_text)
            results.append((surah, ayah, display_text))

    return total, results


def main():
    if len(sys.argv) < 2:
        word = input("Enter Arabic word to search: ").strip()
    else:
        word = " ".join(sys.argv[1:]).strip()

    if not word:
        print("No word provided.")
        sys.exit(1)

    total, results = search(word)

    print(f'\nWord: "{word}"')
    print(f"Total occurrences : {total}")
    print(f"Found in {len(results)} verse(s)\n")

    for surah, ayah, text in results:
        print(f"  [{surah}:{ayah}]  {text}")


if __name__ == "__main__":
    main()
