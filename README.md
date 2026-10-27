# Ofrenda 🌼🕯️

A private, offline **virtual ofrenda** for Día de los Muertos. Write down the stories of the people
you miss, add their favorite foods, songs and flowers, ask questions about them, and build a
candle-lit, printable page. All of it runs on **open-weight models via [Ollama](https://ollama.com)**
on your own machine. No account, no cloud, no internet needed.

> Built for the Hacktoberfest Open-Source AI Challenge, Week 4: *Ghost in the Machine*.

## Why it is careful by design

- **Never pretends to be the person.** The model speaks *about* your loved one, never *as* them.
- **Grounded only in your stories.** `ask` retrieves your own stories first. If none match, the model is not even called, so nothing gets invented.
- **Works with no model.** If Ollama is not running, `remember` and `ask` fall back to simple templates and your stories, so the tool never breaks.
- **Zero dependencies** for the core (Python standard library only). Data is one JSON file you own.

## Quick start

```bash
# 1. open model, running locally
ollama pull llama3.2:3b            # any model works: set OFRENDA_MODEL=qwen2.5:3b, gemma3, etc.

# 2. install
pip install -e .                    # or: pip install -e ".[audio]" for offline voice transcription

# 3. use it
ofrenda add-person "Abuela Rosa" --years "1941-2019" --photo rosa.jpg
ofrenda add-fav    "Abuela Rosa" food "pan de muerto"
ofrenda add-story  "Abuela Rosa" --title "The night the mole burned" --text "She forgot the chocolate..."
ofrenda transcribe "Abuela Rosa" recording.wav --title "Her childhood"   # offline Whisper
ofrenda remember   "Abuela Rosa"                       # writes a remembrance from your stories
ofrenda ask        "Abuela Rosa" "Why did the mole burn?"
ofrenda remember "Abuela Rosa" --speak                 # read aloud, offline (pip install -e ".[voice]")
ofrenda build --out ofrenda.html                       # one self-contained page; print it or share it
```

Try the demo without anything installed: `python -m ofrenda --data examples/demo.json build`.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `OFRENDA_MODEL` | `llama3.2:3b` | Any model Ollama can run |
| `OLLAMA_HOST` | `http://localhost:11434` | Where your model server lives |
| `OFRENDA_DATA` | `ofrenda.json` | Where memories are stored |

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest
```

## CI/CD (GitHub Actions)

- `ci.yml`: lint + tests on Python 3.10 to 3.13, CLI smoke test, builds the package, and on a `v*` tag publishes a GitHub Release with the build files.
- `pages.yml`: builds `examples/demo.json` into a page and deploys it to **GitHub Pages** on every push to `main` (enable *Settings → Pages → Source: GitHub Actions* once).

## License

MIT
