from flask import Flask, render_template, request, jsonify
from pathlib import Path

app = Flask(__name__)

BASE = Path(__file__).parent
CLEAN_FILE = BASE.parent / "quran-simple-clean.txt"
DISPLAY_FILE = BASE / "quran-simple.txt"


def parse_file(path: Path) -> dict[tuple[int, int], str]:
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


# Load both files once at startup
clean_verses = parse_file(CLEAN_FILE)
display_verses = parse_file(DISPLAY_FILE)


def search(word: str) -> dict:
    word = word.strip()
    if not word:
        return {"word": word, "total": 0, "verse_count": 0, "results": []}

    total = 0
    results = []
    for (surah, ayah), clean_text in clean_verses.items():
        count = clean_text.count(word)
        if count:
            total += count
            display_text = display_verses.get((surah, ayah), clean_text)
            results.append({
                "surah": surah,
                "ayah": ayah,
                "text": display_text,
                "count": count,
            })

    return {
        "word": word,
        "total": total,
        "verse_count": len(results),
        "results": results,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search_route():
    word = request.args.get("word", "").strip()
    return jsonify(search(word))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
