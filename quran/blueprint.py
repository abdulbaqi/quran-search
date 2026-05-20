import csv
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
    """Return {surah_number: {name, name_arabic, place}}."""
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
        return {"word": word, "total": 0, "verse_count": 0, "results": []}
    place = place.strip().capitalize()  # "Meccan" | "Medinan" | ""
    total, results = 0, []
    for (surah, ayah), clean_text in _clean.items():
        meta = _toc.get(surah, {})
        if place and meta.get("place") != place:
            continue
        count = clean_text.count(word)
        if count:
            total += count
            results.append({
                "surah": surah,
                "ayah": ayah,
                "surah_name": meta.get("name", ""),
                "surah_name_arabic": meta.get("name_arabic", ""),
                "place": meta.get("place", ""),
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
    place = request.args.get("place", "").strip()
    return jsonify(_search(word, place))
