# GN Light

The fast, lightweight version of [GN 2.0](https://schswork.github.io/math/). Same games, built to load instantly on slow school laptops and networks.

## Why it's fast
- **Tiny cover pictures.** Every cover is pre-shrunk to a 240×180 WebP thumbnail (about 4 KB) stored in `t/`. The original covers average about 200 KB and some are over 10 MB, so the first screen of games is now about 0.25 MB instead of about 10 MB.
- **One small game list.** `games.json` (about 26 KB compressed) replaces the two original lists (about 550 KB), and comes from the same site, so there's no extra connection to set up.
- **Games start downloading when you point at them**, so they open sooner when you click.
- **One small page.** `index.html` holds all the code and styles (about 19 KB, no libraries, no fonts, no build step).
- **Only the games on screen exist.** The grid is virtual: about 50 cards are on the page at any time, whatever the size of the list (the full site draws all ~2,000).
- **Instant repeat visits.** The game list is saved on your device and shown right away, then updated in the background. A tiny `sw.js` keeps a copy of the page so it opens offline.
- **No animations, no accounts, no Firebase, no trackers, no partner (ad) games.**
- Cover pictures load lazily and decode off the main thread.

In testing: first paint about 0.1 s, ~200 page elements (vs ~9,000 on the full site), no freezes while scrolling or searching.

## Features
- Search (with typo tolerance), All / Library / GN Originals / js13k / ★ Favorites / Recent, A–Z or Newest
- 🎲 random game (from what's showing)
- Player with favorite, fullscreen, open in new tab; Esc closes
- <kbd>/</kbd> jumps to search, <kbd>`</kbd> leaves to Google Classroom instantly
- Ad and tracking code is removed from games, same as GN 2.0
- Link straight to a game with `#<id>`, e.g. `…/gn-light/#31`

## Where the games come from
- The gn-math library (`freebuisness/assets` list, `freebuisness/html` game files, `freebuisness/covers`)
- GN Originals from [SCHSwork/GN-originals](https://github.com/SCHSwork/GN-originals)

Every file is tried on jsDelivr, then GitHub, then githack. Games belong to their creators; for removal requests see the full site's DMCA page.

## Keeping it up to date
`tools/build.py` makes `games.json` and the thumbnails from the gn-math library and GN Originals. The **Update games** GitHub Action runs it every day (and can be run by hand from the Actions tab), so new games show up on their own. If `games.json` ever can't load, the page falls back to the original lists.

## Hosting
GitHub Pages: Settings → Pages → Deploy from a branch → `main` / root.
