# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python main.py

# Run the CLI search tool directly
python quran/search_quran.py <arabic-word>

# Production (as deployed on Railway)
gunicorn main:app
```

## Architecture

This is a Flask app structured as a multi-blueprint portal. `main.py` is the entry point — it creates the app, registers the `quran` blueprint, and serves the root portal page (`/`).

**Request flow:**
- `GET /` → `main.py:index()` → `templates/index.html` (portal with app cards)
- `GET /quran/` → `quran/blueprint.py:index()` → `quran/templates/quran/index.html` (search UI)
- `GET /quran/search?word=<arabic>` → `quran/blueprint.py:search()` → JSON `{word, total, verse_count, results[]}`

**Two-file search strategy:** The core design separates search from display. Both text files are loaded into `dict[tuple[int, int], str]` at startup (keyed by `(surah, ayah)`):
- `quran-simple-clean.txt` (root) — diacritics-stripped Arabic; used for string matching
- `quran/quran-simple.txt` — full diacritics; used only for the displayed verse text

This means a user searching for a bare root word (no tashkeel) will match correctly even though the displayed result shows fully vocalized text.

**Text file format:** `surah|ayah|text` — pipe-delimited, three fields per line.

**Frontend highlighting:** `quran/templates/quran/index.html` contains all JS inline. The `buildDiacriticRegex` function inserts a diacritics character-class pattern between every letter of the search word so that the bare search term highlights correctly inside the diacritic-rich display text.

**Unused files:** `quran/app.py` is a standalone Flask app (predates the blueprint refactor) and `quran/templates/index.html` is not referenced by any route — both can be ignored or removed.
