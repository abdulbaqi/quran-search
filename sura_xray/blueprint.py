import unicodedata
from collections import Counter, defaultdict

from flask import Blueprint, jsonify, render_template, request

from quran.data import clean, toc

sura_xray_bp = Blueprint(
    "sura_xray",
    __name__,
    template_folder="templates",
    url_prefix="/sura-xray",
)

BISMILLAH = "بسم الله الرحمن الرحيم "


def _strip_bismillah(surah: int, ayah: int, text: str) -> str:
    if ayah == 1 and text.startswith(BISMILLAH):
        return text[len(BISMILLAH):]
    return text


def _is_arabic_letter(c: str) -> bool:
    return "؀" <= c <= "ۿ" and unicodedata.category(c) == "Lo"


# Build global word→surah index once at startup
_word_surah_index: dict[str, set[int]] = defaultdict(set)
for (_s, _a), _t in clean.items():
    _t = _strip_bismillah(_s, _a, _t)
    for _w in _t.split():
        _word_surah_index[_w].add(_s)


@sura_xray_bp.route("/")
def index():
    return render_template("sura_xray/index.html", toc=toc)


@sura_xray_bp.route("/analyze")
def analyze():
    try:
        surah_num = int(request.args.get("surah", 0))
    except ValueError:
        return jsonify({"error": "invalid surah"}), 400

    if surah_num < 1 or surah_num > 114:
        return jsonify({"error": "surah must be 1–114"}), 400

    surah_info = toc[surah_num]
    verses = {
        ayah: _strip_bismillah(surah_num, ayah, text)
        for (s, ayah), text in clean.items()
        if s == surah_num
    }

    # Stat 1: letter frequency
    all_text = " ".join(verses.values())
    letter_counts: Counter = Counter(c for c in all_text if _is_arabic_letter(c))
    letter_freq = [[letter, count] for letter, count in letter_counts.most_common()]

    # Stat 2: words unique to this surah in the entire Quran
    unique_words = sorted(
        w for w, surahs in _word_surah_index.items()
        if len(surahs) == 1 and surah_num in surahs
    )

    # Stat 3: words appearing more than once within this surah
    word_counter: Counter = Counter()
    for text in verses.values():
        word_counter.update(text.split())
    repeated_words = [
        [w, c] for w, c in word_counter.most_common() if c > 1
    ]

    # Stat 4: longest and shortest verse by word count
    verse_lengths = {ayah: (text, len(text.split())) for ayah, text in verses.items()}
    longest_ayah = max(verse_lengths, key=lambda a: verse_lengths[a][1])
    shortest_ayah = min(verse_lengths, key=lambda a: verse_lengths[a][1])

    return jsonify({
        "surah": surah_num,
        "surah_name": surah_info["name"],
        "surah_name_arabic": surah_info["name_arabic"],
        "verse_count": len(verses),
        "letter_freq": letter_freq,
        "unique_words": unique_words,
        "repeated_words": repeated_words,
        "longest": {
            "ayah": longest_ayah,
            "text": verse_lengths[longest_ayah][0],
            "word_count": verse_lengths[longest_ayah][1],
        },
        "shortest": {
            "ayah": shortest_ayah,
            "text": verse_lengths[shortest_ayah][0],
            "word_count": verse_lengths[shortest_ayah][1],
        },
    })
