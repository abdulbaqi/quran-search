from flask import Blueprint, render_template, request, jsonify
from quran.data import clean as _clean, display as _display, toc as _toc
from quran.data import trans_en as _trans_en, trans_bn as _trans_bn

quran_bp = Blueprint(
    "quran",
    __name__,
    template_folder="templates",
    url_prefix="/quran",
)


def _search(word: str, place: str = "", trans: frozenset = frozenset()) -> dict:
    word = word.strip()
    if not word:
        return {"word": word, "total": 0, "verse_count": 0, "results": []}
    place = place.strip().capitalize()
    total, results = 0, []
    for (surah, ayah), clean_text in _clean.items():
        meta = _toc.get(surah, {})
        if place and meta.get("place") != place:
            continue
        count = clean_text.count(word)
        if count:
            total += count
            entry = {
                "surah": surah,
                "ayah": ayah,
                "surah_name": meta.get("name", ""),
                "surah_name_arabic": meta.get("name_arabic", ""),
                "place": meta.get("place", ""),
                "text": _display.get((surah, ayah), clean_text),
                "count": count,
            }
            if "en" in trans:
                entry["trans_en"] = _trans_en.get((surah, ayah), "")
            if "bn" in trans:
                entry["trans_bn"] = _trans_bn.get((surah, ayah), "")
            results.append(entry)
    return {"word": word, "total": total, "verse_count": len(results), "results": results}


@quran_bp.route("/")
def index():
    return render_template("quran/index.html")


@quran_bp.route("/search")
def search():
    word = request.args.get("word", "").strip()
    place = request.args.get("place", "").strip()
    trans = frozenset(request.args.getlist("trans"))
    return jsonify(_search(word, place, trans))
