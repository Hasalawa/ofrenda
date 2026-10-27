"""Render a self-contained, candle-lit ofrenda page (no external assets)."""

from __future__ import annotations

import base64
import mimetypes
from html import escape
from pathlib import Path

CSS = """
:root{--marigold:#f5a300;--deep:#e0620d;--night:#150b24;--plum:#2a1442;--paper:#fff6e6}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at 50% -10%,#4a2272,var(--night) 60%);
 color:var(--paper);font-family:Georgia,'Times New Roman',serif;line-height:1.6}
header{text-align:center;padding:3rem 1rem 1rem}
h1{font-size:clamp(2rem,6vw,3.4rem);margin:.2rem;color:var(--marigold);letter-spacing:.04em}
.sub{opacity:.8;font-style:italic}
.papel{height:34px;margin:1rem 0;background:
 repeating-linear-gradient(90deg,#f5a300 0 38px,#e0357a 38px 76px,#38b6c9 76px 114px,#8bd450 114px 152px);
 clip-path:polygon(0 0,100% 0,100% 55%,96% 100%,92% 55%,88% 100%,84% 55%,80% 100%,76% 55%,72% 100%,
 68% 55%,64% 100%,60% 55%,56% 100%,52% 55%,48% 100%,44% 55%,40% 100%,36% 55%,32% 100%,28% 55%,
 24% 100%,20% 55%,16% 100%,12% 55%,8% 100%,4% 55%,0 100%);opacity:.9}
main{max-width:980px;margin:auto;padding:1rem;display:grid;gap:2rem}
.card{background:linear-gradient(180deg,var(--plum),#1d0f31);border:1px solid #5a3a85;
 border-radius:18px;padding:1.5rem;box-shadow:0 0 40px #f5a30022}
.top{display:flex;gap:1.2rem;align-items:center;flex-wrap:wrap}
.frame{width:130px;height:160px;border:6px solid var(--marigold);border-radius:8px;
 background:#0004;display:grid;place-items:center;overflow:hidden;font-size:3rem}
.frame img{width:100%;height:100%;object-fit:cover}
h2{margin:0;color:var(--marigold);font-size:1.9rem}
.years{opacity:.7}
.flame{display:inline-block;width:12px;height:22px;background:radial-gradient(#fff 10%,#ffd24a 40%,
 var(--deep) 80%);border-radius:50% 50% 50% 50%/60% 60% 40% 40%;animation:flick 1.4s infinite alternate;
 margin-left:.5rem;filter:drop-shadow(0 0 8px #ffb300)}
@keyframes flick{0%{transform:scale(1,1) rotate(-3deg)}50%{transform:scale(.9,1.1) rotate(2deg)}
 100%{transform:scale(1.05,.95) rotate(-1deg)}}
.remembrance{font-size:1.15rem;border-left:4px solid var(--deep);padding-left:1rem;margin:1.2rem 0}
.favs{display:flex;gap:.5rem;flex-wrap:wrap;margin:.8rem 0}
.chip{background:#f5a30022;border:1px solid var(--marigold);border-radius:999px;padding:.2rem .8rem;font-size:.95rem}
details{background:#0003;border-radius:10px;padding:.7rem 1rem;margin:.6rem 0}
summary{cursor:pointer;color:var(--marigold);font-weight:bold}
footer{text-align:center;opacity:.65;padding:2rem 1rem 3rem;font-size:.9rem}
@media print{body{background:#fff;color:#000}.card{box-shadow:none;border-color:#999;background:#fff}
 h1,h2,summary{color:#a64b00}.papel,.flame{display:none}}
"""


def _photo_tag(person: dict, base: Path | None) -> str:
    path = person.get("photo")
    if path:
        p = Path(path)
        if not p.is_absolute() and base:
            p = base / p
        if p.is_file():
            mime = mimetypes.guess_type(p.name)[0] or "image/jpeg"
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            return f'<img alt="{escape(person["name"])}" src="data:{mime};base64,{b64}">'
    return "&#127804;"  # blossom


def _chips(items: list[str], icon: str) -> str:
    return "".join(f'<span class="chip">{icon} {escape(i)}</span>' for i in items)


def render_html(data: dict, base: Path | None = None, title: str = "Ofrenda") -> str:
    cards = []
    for person in data["people"]:
        fav = person["favorites"]
        chips = (
            _chips(fav.get("foods", []), "&#127858;")
            + _chips(fav.get("songs", []), "&#127925;")
            + _chips(fav.get("flowers", []), "&#127802;")
        )
        stories = "".join(
            f"<details><summary>{escape(s['title'])}</summary>"
            f"<p>{escape(s['text'])}</p></details>"
            for s in person["stories"]
        )
        remembrance = (
            f'<p class="remembrance">{escape(person["remembrance"])}</p>'
            if person.get("remembrance")
            else ""
        )
        cards.append(
            f"""<section class="card"><div class="top">
<div class="frame">{_photo_tag(person, base)}</div>
<div><h2>{escape(person["name"])}<span class="flame"></span></h2>
<div class="years">{escape(person.get("years", ""))}</div></div></div>
{remembrance}<div class="favs">{chips}</div>{stories}</section>"""
        )
    body = "\n".join(cards) or "<p style='text-align:center'>No one here yet.</p>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><style>{CSS}</style></head>
<body><header><h1>{escape(title)}</h1>
<div class="sub">Those we remember never really leave.</div></header>
<div class="papel"></div><main>{body}</main>
<footer>Written locally with open-weight models. These memories never left this machine.</footer>
</body></html>
"""
