"""Render Reflecka social slides to PNG.

Usage: python render.py slides.json out_dir [--reel]
Default is 1080x1350 (Instagram carousel). --reel renders 1080x1920 frames.
"""
import json, sys, html, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent.resolve()

CSS = """
@font-face{font-family:'Space Grotesk';src:url('file://%(d)s/SpaceGrotesk.ttf');font-weight:300 700}
@font-face{font-family:'JetBrains Mono';src:url('file://%(d)s/JetBrainsMono.ttf');font-weight:100 800}
:root{--bg:#0a0e1a;--card:#111827;--line:rgba(255,255,255,.09);--text:#e6edf3;--muted:#8b9bb4;
      --blue:#a8d8f0;--orange:#f2a15f;--grid:rgba(120,150,210,.07)}
*{box-sizing:border-box;margin:0}
html,body{width:%(w)dpx;height:%(h)dpx;background:var(--bg);color:var(--text);
  font-family:'Space Grotesk',sans-serif;overflow:hidden}
body{background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);
  background-size:90px 90px;background-position:center}
.frame{position:relative;width:100%%;height:100%%;padding:72px 80px;display:flex;flex-direction:column}
.top{display:flex;justify-content:space-between;align-items:center}
.brand{display:flex;align-items:center;gap:18px;font-weight:600;font-size:38px;letter-spacing:-.01em}
.brand img{width:60px;height:60px;border-radius:50%%;border:2px solid rgba(255,255,255,.18);background:#131a2b}
.count{font-family:'JetBrains Mono',monospace;font-size:28px;color:var(--text)}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;gap:40px}
.kicker{font-family:'JetBrains Mono',monospace;font-size:30px;color:var(--orange)}
.kicker.blue{color:var(--blue)}
h1{font-size:%(t)dpx;line-height:1.05;letter-spacing:-.025em;font-weight:600;white-space:pre-line}
h1.hero{font-size:%(th)dpx}
p.body{font-size:42px;line-height:1.35;color:var(--text);max-width:26ch}
.card{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:40px 44px;
  font-family:'JetBrains Mono',monospace;font-size:34px;line-height:1.55;white-space:pre;overflow:hidden;
  box-shadow:0 30px 80px rgba(0,0,0,.45)}
.card .hl{background:rgba(242,161,95,.18);border-left:6px solid var(--orange);margin-left:-44px;padding-left:38px;display:block}
.card .ok{background:rgba(168,216,240,.14);border-left:6px solid var(--blue);margin-left:-44px;padding-left:38px;display:block}
.card .c{color:var(--text);opacity:.85}
.quote{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:44px 48px;font-size:44px;line-height:1.35;
  position:relative;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.quote.a{border-top:6px solid var(--orange)}.quote.b{border-top:6px solid var(--blue)}
.quote .who{font-family:'JetBrains Mono',monospace;font-size:28px;color:var(--text);margin-bottom:18px}
.score{display:flex;flex-direction:column;gap:18px}
.row{display:flex;align-items:center;gap:24px;font-family:'JetBrains Mono',monospace;font-size:30px}
.row span{width:9ch;color:var(--muted)}
.row i{flex:1;height:14px;background:rgba(255,255,255,.08);border-radius:7px;overflow:hidden;display:block}
.row i b{display:block;height:100%%;background:var(--blue);border-radius:7px}
.row em{width:4ch;text-align:right;font-style:normal}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:30px 22px;text-align:center}
.tile.g{border-color:rgba(110,220,170,.45)}.tile.o{border-color:rgba(242,161,95,.5)}
.tile .n{font-size:66px;font-weight:600;letter-spacing:-.02em;line-height:1}
.tile.g .n{color:#7fe0b4}.tile.o .n{color:var(--orange)}
.tile .l{font-size:28px;margin-top:10px}
.tile .h{font-family:'JetBrains Mono',monospace;font-size:22px;color:var(--text);margin-top:8px}
.tile .h::before{content:'● ';font-size:14px;vertical-align:middle}
.tile.g .h::before{color:#7fe0b4}.tile.o .h::before{color:var(--orange)}
.apptitle{font-size:84px;font-weight:600;color:var(--orange);letter-spacing:-.02em;line-height:1}
.sub{font-size:46px;line-height:1.3;color:var(--text);max-width:22ch}
.naomi{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:36px 40px;display:flex;gap:26px;align-items:flex-start;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.naomi .av{flex:none;width:68px;height:68px;border-radius:50%%;background:#2a2118;border:2px solid var(--orange);color:var(--orange);display:flex;align-items:center;justify-content:center;font-weight:600;font-size:34px}
.naomi .nm{font-weight:600;font-size:30px;margin-bottom:8px}
.naomi .tx{font-size:32px;line-height:1.35;color:var(--text)}
.chip{display:inline-flex;align-items:center;gap:16px;font-family:'JetBrains Mono',monospace;font-size:28px;padding:18px 26px;border-radius:14px;align-self:flex-start}
.chip.fail{background:rgba(255,90,90,.12);border:1px solid rgba(255,90,90,.45)}.chip.fail b{color:#ff6b6b}
.chip.pass{background:rgba(127,224,180,.12);border:1px solid rgba(127,224,180,.45)}.chip.pass b{color:#7fe0b4}
.cta{display:inline-block;background:var(--blue);color:#0a0e1a;font-weight:600;font-size:36px;padding:26px 44px;border-radius:16px;align-self:flex-start}
.bot{display:flex;justify-content:space-between;align-items:center;gap:40px}
.bar{flex:1;height:8px;background:rgba(255,255,255,.08);border-radius:4px;overflow:hidden}
.bar b{display:block;height:100%%;background:linear-gradient(90deg,var(--blue),var(--orange));border-radius:4px}
.site{font-family:'JetBrains Mono',monospace;font-size:26px;color:var(--text)}
"""

def block(kind, v):
    e = html.escape
    if kind == "kicker":  return f'<div class="kicker">{e(v)}</div>'
    if kind == "kicker_blue": return f'<div class="kicker blue">{e(v)}</div>'
    if kind == "h1":      return f'<h1>{e(v)}</h1>'
    if kind == "hero":    return f'<h1 class="hero">{e(v)}</h1>'
    if kind == "body":    return f'<p class="body">{e(v)}</p>'
    if kind == "cta":     return f'<div class="cta">{e(v)}</div>'
    if kind == "code":
        out = []
        for line in v:
            if isinstance(line, list):
                out.append(f'<span class="{line[0]}">{e(line[1])}</span>')
            else:
                out.append(e(line))
        return '<div class="card">' + "\n".join(out) + '</div>'
    if kind == "quote":
        return f'<div class="quote {v["cls"]}"><div class="who">{e(v["who"])}</div>{e(v["text"])}</div>'
    if kind == "score":
        rows = "".join(
            f'<div class="row"><span>{e(n)}</span><i><b style="width:{s}%"></b></i><em>{s}</em></div>' for n, s in v)
        return f'<div class="score">{rows}</div>'
    if kind == "apptitle": return f'<div class="apptitle">{e(v)}</div>'
    if kind == "sub": return f'<p class="sub">{e(v)}</p>'
    if kind == "naomi": return f'<div class="naomi"><div class="av">N</div><div><div class="nm">Naomi — Technical Coach</div><div class="tx">{e(v)}</div></div></div>'
    if kind == "chip": return f'<div class="chip {v[0]}"><b>{e(v[1])}</b>{e(v[2])}</div>'
    if kind == "metrics":
        tiles = "".join(f'<div class="tile {c}"><div class="n">{e(n)}</div><div class="l">{e(l)}</div><div class="h">{e(h)}</div></div>' for c,n,l,h in v)
        return f'<div class="metrics">{tiles}</div>'
    raise ValueError(kind)

def page(slide, i, n, w, h):
    mid = "".join(block(k, v) for k, v in slide)
    t, th = (72, 104) if h > 1400 else (66, 96)
    css = CSS % {"d": HERE, "w": w, "h": h, "t": t, "th": th}
    pct = int(100 * (i + 1) / n)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="frame">
 <div class="top"><div class="brand"><img src="file://{HERE}/icon.png">Reflecka</div><div class="count">{i+1:02d} / {n:02d}</div></div>
 <div class="mid">{mid}</div>
 <div class="bot"><div class="bar"><b style="width:{pct}%"></b></div><div class="site">reflecka.com</div></div>
</div></body></html>"""

def main():
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    reel = "--reel" in sys.argv
    w, h = (1080, 1920) if reel else (1080, 1350)
    slides = json.loads(src.read_text())
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        for i, s in enumerate(slides):
            pg.set_content(page(s, i, len(slides), w, h))
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(out / f"slide-{i+1:02d}.png"))
        b.close()
    print(f"wrote {len(slides)} slides to {out}")

if __name__ == "__main__":
    main()
