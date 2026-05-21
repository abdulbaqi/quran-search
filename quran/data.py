import csv
import json
from pathlib import Path

BASE = Path(__file__).parent


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


def _load_translation(path: Path) -> dict[tuple[int, int], str]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {(item["chapter"], item["verse"]): item["text"]
            for item in data.get("quran", [])}


clean = _parse(BASE.parent / "quran-simple-clean.txt")
display = _parse(BASE / "quran-simple.txt")
toc = _load_toc(BASE.parent / "quran-toc.csv")

_en_path = BASE / "eng-mustafakhattaba.json"
_bn_path = BASE / "ben-abubakrzakaria.json"
trans_en = _load_translation(_en_path) if _en_path.exists() else {}
trans_bn = _load_translation(_bn_path) if _bn_path.exists() else {}
