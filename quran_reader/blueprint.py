from flask import Blueprint, render_template, redirect, url_for
from quran.data import display, toc, trans_en, trans_bn

reader_bp = Blueprint(
    "reader",
    __name__,
    template_folder="templates",
    url_prefix="/read",
)

# Surahs where Tanzil numbers the Bismillah as verse 1 but translations do not.
# Excludes surah 1 (Bismillah IS the canonical verse 1 in all systems)
# and surah 9 (no Bismillah).
_BISMILLAH_SURAHS = set(range(2, 115)) - {9}


def _surah_verses(surah: int) -> list[dict]:
    pairs = sorted(
        [(a, t) for (s, a), t in display.items() if s == surah],
        key=lambda x: x[0],
    )
    offset = 1 if surah in _BISMILLAH_SURAHS else 0
    result = []
    for ayah, arabic in pairs:
        trans_ayah = ayah - offset
        entry = {
            "ayah": ayah,
            "display_ayah": trans_ayah if trans_ayah >= 1 else ayah,
            "arabic": arabic,
            "is_bismillah": offset == 1 and ayah == 1,
            "trans_en": trans_en.get((surah, trans_ayah), "") if trans_ayah >= 1 else "",
            "trans_bn": trans_bn.get((surah, trans_ayah), "") if trans_ayah >= 1 else "",
        }
        result.append(entry)
    return result


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
