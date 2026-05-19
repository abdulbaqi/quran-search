from flask import Blueprint, render_template, request, jsonify
from pathlib import Path

quran_bp = Blueprint(
    "quran",
    __name__,
    template_folder="templates",
    url_prefix="/quran",
)

BASE = Path(__file__).parent
CLEAN_FILE = BASE.parent / "quran-simple-clean.txt"
DISPLAY_FILE = BASE / "quran-simple.txt"


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


_clean = _parse(CLEAN_FILE)
_display = _parse(DISPLAY_FILE)


def _search(word: str) -> dict:
    word = word.strip()
    if not word:
        return {"word": word, "total": 0, "verse_count": 0, "results": []}
    total, results = 0, []
    for (surah, ayah), clean_text in _clean.items():
        count = clean_text.count(word)
        if count:
            total += count
            results.append({
                "surah": surah,
                "ayah": ayah,
                "text": _display.get((surah, ayah), clean_text),
                "count": count,
            })
    return {"word": word, "total": total, "verse_count": len(results), "results": results}


@quran_bp.route("/")
def index():
    return render_template("quran/index.html")


@quran_bp.route("/search")
def search():
    word = request.args.get("word", "").strip()
    return jsonify(_search(word))
