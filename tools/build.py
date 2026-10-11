#!/usr/bin/env python3
"""Builds GN Light's game list and cover thumbnails.

  games.json   one small list of every game: [id, name, kind, file, has_thumb, cover?]
  t/<id>.webp  240x180 thumbnails (a few KB each instead of ~200 KB covers)

Run with no arguments to download everything it needs (the GitHub Action does
this every day). For local runs you can point it at copies you already have:
  python3 tools/build.py --zones zones.json --covers covers/ --originals ../GN-originals
Only games without a thumbnail yet are downloaded and resized.
"""
import argparse, io, json, pathlib, re, sys, urllib.request
from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
THUMBS = ROOT / "t"
W, H = 240, 180
# The game library is pinned to its last clean version (keep in sync with LIB in
# index.html). Games without a file in that version are left out.
LIB_REF = "48c0631289237dd2e9e202fde532edfae4ed2acf"

def pinned_files(path=None):
    if path:
        return set(json.loads(pathlib.Path(path).read_text())["files"])
    tree = json.loads(get(f"https://api.github.com/repos/freebuisness/html/git/trees/{LIB_REF}"))
    return {t["path"] for t in tree["tree"] if t["path"].endswith(".html")}

def pinned_file_for(files, gid):
    cands = [f for f in files if re.match(rf"^{gid}(?:[-.]|$)", f)]
    fix = lambda n: int(m.group(1) or 1) if (m := re.search(r"-fix(\d*)", n)) else 0
    return max(cands, key=fix) if cands else None

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gn-light-build"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def thumb(data, out):
    im = Image.open(io.BytesIO(data))
    im.seek(0)
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (27, 30, 38, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    im = ImageOps.fit(im, (W, H), Image.LANCZOS, centering=(0.5, 0.4))
    im.save(out, "WEBP", quality=58, method=6)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zones"); ap.add_argument("--covers"); ap.add_argument("--originals"); ap.add_argument("--pinned")
    a = ap.parse_args()
    THUMBS.mkdir(exist_ok=True)

    zones = json.loads(pathlib.Path(a.zones).read_text() if a.zones else get("https://raw.githubusercontent.com/freebuisness/assets/main/zones.json"))
    og_dir = pathlib.Path(a.originals) if a.originals else None
    originals = json.loads((og_dir / "games.json").read_text() if og_dir else get("https://raw.githubusercontent.com/SCHSwork/GN-originals/main/games.json"))

    pinned = pinned_files(a.pinned)
    games, made, failed, hidden = [], 0, [], 0
    def add(gid, name, kind, file, cover_src, load):
        nonlocal made
        out = THUMBS / f"{gid}.webp"
        if not out.exists() and cover_src:
            try:
                thumb(load(cover_src), out); made += 1
            except Exception as e:
                failed.append(f"{gid} {name}: {e}")
        games.append([gid, name, kind, file, 1 if out.exists() else 0])

    for z in zones:
        name = str(z.get("name") or "").strip()
        url = z.get("url") or ""
        if not name or re.match(r"^\[!\]", name) or re.search(r"comment|discord", name, re.I) or url.startswith("http"):
            continue
        file = url.replace("{HTML_URL}/", "").replace("{HTML_URL}", "")
        if file not in pinned:
            file = pinned_file_for(pinned, int(z["id"]))
            if not file:
                hidden += 1; continue
        cover = (z.get("cover") or "").replace("{COVER_URL}/", "").replace("{COVER_URL}", "")
        load = (lambda p: (pathlib.Path(a.covers) / p).read_bytes()) if a.covers else (lambda p: get("https://raw.githubusercontent.com/freebuisness/covers/main/" + p))
        add(int(z["id"]), name, 0, file, cover, load)

    lib_ids = {g[0] for g in games}
    for z in originals:
        if not z.get("name") or z.get("libraryDuplicate") or int(z["id"]) in lib_ids or ".." in str(z.get("path", "")):
            continue
        kind = 2 if "js13k" in (z.get("special") or []) else 1
        load = (lambda p: (og_dir / p).read_bytes()) if og_dir else (lambda p: get("https://raw.githubusercontent.com/SCHSwork/GN-originals/main/" + p))
        add(int(z["id"]), z["name"].strip(), kind, z["path"], z.get("cover") or "", load)

    games.sort(key=lambda g: g[0])
    (ROOT / "games.json").write_text(json.dumps(games, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(games)} games, {made} new thumbnails, {sum(g[4] for g in games)} with thumbnails, {hidden} library games left out (not in the clean version)")
    for f in failed[:20]: print("  no thumbnail:", f, file=sys.stderr)

if __name__ == "__main__":
    main()
