import os
import urllib.request
from pathlib import Path
from flask import Flask, render_template

_BASE = Path(__file__).parent
_RAW = "https://raw.githubusercontent.com/abdulbaqi/quran-search/main"
_CDN = "https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions"

_FILES = {
    _BASE / "quran-simple-clean.txt": f"{_RAW}/quran-simple-clean.txt",
    _BASE / "quran" / "quran-simple.txt": f"{_RAW}/quran/quran-simple.txt",
    _BASE / "quran" / "eng-mustafakhattaba.json": f"{_CDN}/eng-mustafakhattaba.json",
    _BASE / "quran" / "ben-abubakrzakaria.json": f"{_CDN}/ben-abubakrzakaria.json",
}

for path, url in _FILES.items():
    if not path.exists():
        print(f"Downloading {path.name} …")
        urllib.request.urlretrieve(url, path)

from quran.blueprint import quran_bp
from quran_reader.blueprint import reader_bp
from sura_xray.blueprint import sura_xray_bp
from word_neighbour.blueprint import word_neighbour_bp

app = Flask(__name__)
app.register_blueprint(reader_bp)
app.register_blueprint(quran_bp)
app.register_blueprint(sura_xray_bp)
app.register_blueprint(word_neighbour_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, port=port)
