# Cuba (The Dice System)

Cuba is Ruby's cube planet, the second world of The Dice System after Tetra. Read `../tetra/CLAUDE.md` first: its ground rules are the rules here too (canon comes from Ruby by chat, relayed by Joshua; never invent canon, mark every reading as a reading; no em dashes anywhere, `make audit` fails on them; test before shipping; Ruby's spellings exactly). Then read `HANDOFF.md` here (state, the canon ledger, the open questions). Joshua is the client; Ruby is the author.

## What exists (draft 1, 2026-10-04)

A WebGL cube with six square sides. Only the Canon side is drawn: Ruby's central island (a broad cross with rounded bends at the corners) whose four arms reach the sides and connect onto the East, West, North and South sides (her words), with the small hole in its middle that takes you through the world to the Far side. On those four sides the land continues a short way (`TONGUE`, a reading) and the rest is uncharted slate; the Far side carries the hole's other end and nothing else. A Codex panel holds the World tab (her words and the readings), the six sides and a card per side or place. No calendar, star, moon or fields: nothing has been said about them for Cuba.

The island is drawn from a written description of Ruby's photo, not from the photo itself (it had not reached the repository); the shape is to be checked against the photo when it arrives (`reference/ruby/README.md`).

## Layout

```
CLAUDE.md, HANDOFF.md, Makefile, package.json
pipeline/
  mapgen.py          the face textures: map_canon.jpg (the island and the hole), map_east/west/north/south.jpg (the island's arm continuing onto that side, `TONGUE`, then uncharted slate), map_far.jpg (the hole's other end), map_blank.jpg (uncharted), anchors.json (marker positions), map_canon_prev.png (markers drawn)
  template.html      the whole page (CSS + HTML + JS) with {{TEX_CANON}}, {{TEX_EAST}}, {{TEX_WEST}}, {{TEX_NORTH}}, {{TEX_SOUTH}}, {{TEX_FAR}}, {{TEX_BLANK}}, {{ANCHORS}}
  build.py           inlines them -> dist/cuba.html (fragment, published to the artifact) and dist/cuba_world.html (standalone)
dist/                build outputs, committed
tests/               _page.js (Playwright from ../node_modules or ../../tetra/node_modules), smoke.js; screenshots land in tests/out/
tools/audit.py       em dashes and placeholders
reference/ruby/      Ruby's pictures for Cuba (none received yet)
```

## Build, test, ship

```
make maps      # cd pipeline && python3 mapgen.py   (deterministic, asserts: one piece of land, arms reaching the middle of each side, corners water, the hole in the middle, the land agreeing across the four edges)
make build     # python3 pipeline/build.py
make test      # rebuilds, then tests/smoke.js: no errors at 1366 and 393 px, six sides in Ruby's arrangement, the island and hole markers, the phone Codex opens on a side tap
make audit     # must print 'audit clean'
```

Python 3.11 with numpy, OpenCV (`opencv-python-headless<5`) and Pillow from `../tetra/requirements.txt`; Playwright from `../tetra` (`npm install` there). Ship both `dist/cuba.html` (republish to the Cuba artifact, URL in HANDOFF.md) and `dist/cuba_world.html`.

## Geometry conventions

- Cube of half-size 1 at the origin, spinning about the North-South axis (Y). `FACES` in the template: `canon` +Z, `far` -Z, `west` +X, `east` -X, `north` +Y (top), `south` -Y (bottom). Each face has a `right` and an `up` vector; texture row 0 is the top of the face, column 0 its left.
- Ruby's arrangement (her net: East, Canon, West, Far in a row, North above Canon, South below): looking at Canon with North up, East is on the LEFT and West on the RIGHT, Far behind. So `east` is -X and `west` is +X. Keep it; it is hers. North's `up` points toward Far, South's `up` toward Canon, as the net unfolds.
- Face textures are 1024 x 1024 px. The tongue texture is drawn once with the land at the top edge and rotated per side (East: right edge, West: left, North: bottom, South: top, the edges each shares with Canon). `anchors.json` holds marker positions in face px per side. `facePoint(side, px, py)` in the template maps them onto the cube.
- Which way Cuba turns, and how fast, is unwritten; the spin is a placeholder (`state.spin += dt*speed*0.12`).

## template.html, where things are

`WORLD` (sides, places, lore: her words verbatim), `FACES`, the shaders `VS`/`FS` (one directional light, no star story), `buildMarkers`/`updateMarkers`, the Codex (`showTab`, `openCodex`, `renderSides`, `renderPlace`, `selectSide`, `selectPlace`), the dock (six face buttons from `WORLD.sides`, Codex, Pause/Spin, Reset), pointer handling (drag turns, wheel zooms, a tap on the world selects the facing side), the frame loop, and the debug hook `window.cuba = {state, face(id, fly), facing(), neighbours(), markers(), setSpin(on), select(id)}` used by the tests. `neighbours()` reports which side is left, right, up, down and behind the facing side on screen. Hot reload (`window.claude.hot`) restores spin, camera and play state, as Tetra does.

## How a round from Ruby is processed

As for Tetra (`../tetra/CLAUDE.md`, last section): her words verbatim into `HANDOFF.md` first, the literal reading noted, then maps (`mapgen.py`), page (`WORLD` and the World tab in `template.html`), `make maps && make build && make test && make audit`, look at `tests/out/*.png` and `pipeline/map_canon_prev.png`, ship both files, report in her terms.
