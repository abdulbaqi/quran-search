from flask import Blueprint, render_template, redirect, url_for
from quran.data import display, toc, trans_en, trans_bn

reader_bp = Blueprint(
    "reader",
    __name__,
    template_folder="templates",
    url_prefix="/read",
)


def _surah_verses(surah: int) -> list[dict]:
    pairs = sorted(
        [(a, t) for (s, a), t in display.items() if s == surah],
        key=lambda x: x[0],
    )
    return [
        {
            "ayah": ayah,
            "arabic": arabic,
            "trans_en": trans_en.get((surah, ayah), ""),
            "trans_bn": trans_bn.get((surah, ayah), ""),
        }
        for ayah, arabic in pairs
    ]


@reader_bp.route("/")
def index():
    return redirect(url_for("reader.surah", surah=1))


@reader_bp.route("/<int:surah>")
@reader_bp.route("/<int:surah>/<int:ayah>")
def surah(surah: int, ayah: int = None):
    if surah < 1 or surah > 114:
        return redirect(url_for("reader.surah", surah=1))
    meta = toc.get(surah, {})
    verses = _surah_verses(surah)
    return render_template(
        "reader/index.html",
        surah=surah,
        meta=meta,
        verses=verses,
        toc=toc,
        scroll_to=ayah,
    )
