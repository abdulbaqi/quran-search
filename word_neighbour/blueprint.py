import csv
from collections import Counter
from flask import Blueprint, render_template, request, jsonify
from pathlib import Path

word_neighbour_bp = Blueprint(
    "word_neighbour",
    __name__,
    template_folder="templates",
    url_prefix="/word-neighbour",
)

BASE = Path(__file__).parent
CLEAN_FILE = BASE.parent / "quran-simple-clean.txt"
DISPLAY_FILE = BASE.parent / "quran" / "quran-simple.txt"
TOC_FILE = BASE.parent / "quran-toc.csv"


def _parse(path: Path) -> dict[tuple[int, int], str]:
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


def _load_toc(path: Path) -> dict[int, dict]:
    toc = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            toc[int(row["No."])] = {
                "name": row["Name"],
                "name_arabic": row["Name Arabic"],
                "place": row["Place"],
            }
    return toc


_clean = _parse(CLEAN_FILE)
_display = _parse(DISPLAY_FILE)
_toc = _load_toc(TOC_FILE)


def _search(word: str, place: str = "") -> dict:
    word = word.strip()
    if not word:
        return {"word": word, "total": 0, "results": [], "left_freq": [], "right_freq": []}

    place = place.strip().capitalize()
    left_counter: Counter = Counter()
    right_counter: Counter = Counter()
    results = []

    for (surah, ayah), clean_text in _clean.items():
        meta = _toc.get(surah, {})
        if place and meta.get("place") != place:
            continue
        words = clean_text.split()
        for i, w in enumerate(words):
            if w != word:
                continue
            left_word = words[i - 1] if i > 0 else None
            right_word = words[i + 1] if i < len(words) - 1 else None
            if left_word:
                left_counter[left_word] += 1
            if right_word:
                right_counter[right_word] += 1
            left_ctx = " ".join(words[max(0, i - 5):i])
            right_ctx = " ".join(words[i + 1:i + 6])
            results.append({
                "surah": surah,
                "ayah": ayah,
                "surah_name": meta.get("name", ""),
                "surah_name_arabic": meta.get("name_arabic", ""),
                "place": meta.get("place", ""),
                "left": left_ctx,
                "right": right_ctx,
                "text": _display.get((surah, ayah), clean_text),
            })

    return {
        "word": word,
        "total": len(results),
        "results": results,
        "left_freq": left_counter.most_common(10),
        "right_freq": right_counter.most_common(10),
    }


@word_neighbour_bp.route("/")
def index():
    return render_template("word_neighbour/index.html")


@word_neighbour_bp.route("/search")
def search():
    word = request.args.get("word", "").strip()
    place = request.args.get("place", "").strip()
    return jsonify(_search(word, place))
