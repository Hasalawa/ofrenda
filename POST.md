---
title: "Ofrenda: a private, offline ofrenda that remembers with open-weight models"
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

**Ofrenda** is a local-first virtual ofrenda for Día de los Muertos. You write down the stories of people you miss, add their favorite foods, songs and flowers, and an open-weight model running on your own machine helps you turn them into a remembrance. You can also ask questions ("Why did the mole burn?") and get answers grounded **only** in the stories you wrote. `ofrenda serve` opens a candle-lit altar in the browser (falling marigold petals, papel picado, flickering candles) where you talk with a gentle AI companion whose answers stream in live and can be read aloud. It can also export one self-contained, printable HTML page.

I read "Ghost in the Machine" gently: not a ghost that haunts, but the people who stay with us through the stories we keep. Two design rules came from that:

- The model speaks *about* your loved one, never *as* them. No fake séance with someone you actually miss.
- If no story matches a question, the model is not called at all, so nothing gets invented.

## Demo

<!-- Add your GitHub Pages link: https://<your-username>.github.io/ofrenda/ -->

## Code

{% embed https://github.com/<your-username>/ofrenda %}

## How I Built It

- **Model:** any open-weight model served by [Ollama](https://ollama.com) (default `llama3.2:3b`, switch with `OFRENDA_MODEL`).
- **Retrieval:** a tiny keyword matcher over your stories, so a 3B model on a laptop only sees what matters.
- **Web app:** a zero-dependency Python server bound to `127.0.0.1` with a streaming `/api/ask`, and a single offline HTML page (no CDN, no tracking).
- **Voice (optional):** `faster-whisper` transcribes a recorded family story fully offline.
- **Core:** Python standard library only, one JSON file for data, one HTML file for output.
- **Graceful fallback:** with no model running, `remember` and `ask` still work using templates and your own stories.
- **CI/CD:** GitHub Actions for lint and tests on Python 3.10 to 3.13, packaged releases on tags, and the demo page deployed to GitHub Pages.

## Why Does Open Innovation Matter?

Family stories are the most private data there is. With a closed API, grandma's stories would be uploaded to a server I do not control, and the project would stop working the day that service changes or disappears. With an open-weight model on my laptop:

- It works with the lights and the internet off.
- Nothing leaves the machine.
- I can swap the model (or fine-tune one on a family's own language, including dialects a big model handles poorly).
- It costs nothing to run, so anyone can use it.

## My Agent Session

<!-- Optional: embed your DevRelay session here. -->

## The Spirit of It

<!-- Add the moment it landed: the first time a real story came back as a remembrance. Or remove this section. -->

## Prize Categories

<!-- List any partner categories you are entering, or remove this section. -->
