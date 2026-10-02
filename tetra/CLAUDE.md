# Tetra (The Dice System)

Tetra is a four-sided world: an interactive WebGL tetrahedron, one map per face, a day/night cycle, a 13-month calendar and a "Codex" side panel of places, nations and lore. It is Ruby's world (Joshua's child). **Canon comes from Ruby, by chat, relayed by Joshua. Nothing here is invented beyond what she has said; where the build had to guess, the guess is marked as a guess in the Codex ("Still unwritten", "not yet written").** Joshua is the client; Ruby is the author.

Shipped state: **version 10** (2026-10-02). `dist/tetra_world.html` is the single-file build of that version. The published copy lives at `https://claude.ai/artifact/G6JjTxacMzAGCtcSrETb8v` (private artifact, republished from `dist/tetra.html`, see "Shipping" below). Read `HANDOFF.md` for the state, the change ledger and the open questions.

## Ground rules (Joshua's, and they are firm)

1. **Never invent canon.** Ruby's words are the source. If a request is ambiguous, implement the most literal reading and say which reading was taken. Draft lore (`WORLD.lore` in the template) is first-pass text for Joshua to edit, and it is labelled as such in the page.
2. **No em dashes anywhere** in copy, code comments, docs or commit messages. Use commas, periods, parentheses, or restructure. `make audit` (tools/audit.py) fails on any em dash in the sources, the docs or `dist/` (base64 stripped), and on retired names and unreplaced placeholders.
3. **Test before shipping. Every time.** Joshua is not the test bed. Minimum: `npm test` passes (no script or console errors at 1366 px and 393 px, Far-face phase rules hold, phone tap opens the Codex), plus eyeball the screenshots in `tests/out/` and the seam sheet from `npm run seams` after any map change.
4. **Every face is at least half water** (`mapgen2.py` asserts it) and **every marker sits on land** (asserted too). Landmasses line up across every edge (`check_edges.py`; v10 ships with the worst edge at 3.7% disagreement, so treat anything above about 5% as a regression).
5. **Use Ruby's outlines, not the explorers' pictures.** In-world, the explorers Sapphire, Amethyst and Obsidian made rough charts and Opal "went back and made complete maps". The page shows Opal's maps (generated from the sketches), never the sketch photos.
6. Names are spelled exactly as Ruby spells them (`It's Hot` is the nation's full name; `Marshia`, `Baiuland`, `Greeneria`, `Wetia`, `Tredesember`).
7. Deliverables each round: the republished artifact (same URL) **and** the standalone `dist/tetra_world.html`.

## Repo layout

```
CLAUDE.md, HANDOFF.md, README.md      this file, the state/ledger, the quickstart
Makefile, package.json, requirements.txt
pipeline/                            everything that makes the page; scripts run with cwd = pipeline/
  template.html                      the whole app (CSS + HTML + JS) with {{PLACEHOLDERS}} for textures and geometry
  build.py                           inlines textures/geometry into template.html -> dist/tetra.html + dist/tetra_world.html
  mapgen2.py                         CURRENT map designer for West, South, Far (writes map_*.jpg, codex_*.jpg, map_anchors.json)
  mapgen.py                          helpers (noise, masks, labels, rivers, Codex crops) + the first-pass designer (superseded)
  edges.py                           shared-edge land/water profiles and conform(); caches to edge_profiles.json
  paintface.py                       turns a height design into painted terrain (land layer + sea layer, cut on the coastline)
  texsynth.py                        patch-quilting texture synthesis from the Canon art (art_latest.png)
  blobs.py                           Ruby's outlines (continent, central island) typed in by hand, in texture space
  nations.py                         where the island / continent nations sit (shared by mapgen2 and build)
  bake.py, radial.py                 Canon face: warps Ruby's painting (art_latest.png) into tex_canon.jpg + geometry.json
  check_edges.py                     measures land/water agreement along the six edges -> edge_check.png
  art_latest.png                     Ruby's Canon painting (1448x1086). Source of the Canon texture AND of all terrain patches
  tex_canon.jpg, geometry.json       outputs of bake.py (Canon texture, face layouts, Canon region barycentrics)
  map_{west,south,far}.jpg           outputs of mapgen2.py: the face textures (no labels; labels are HTML markers)
  codex_{west,south,far,island,continent}.jpg   labelled Codex charts (Opal's maps)
  map_anchors.json                   marker positions in texture px per face (mapgen2 -> build)
  edge_profiles.json                 CACHE of edge profiles. Delete it after changing tex_canon.jpg or the designed intervals
  blobs.json, water_fractions.json, west_places.json, south_far_places.json   small data files (see "Pipeline")
  zinnia_q.png                       the Umbrella Tree Zinnia cutout shown in the Codex
  fonts/Lora-*.ttf                   label fonts for the Codex charts (OFL)
  legacy/                            sketch-processing scripts from earlier rounds (not in the build path)
dist/                                build outputs (committed so the shipped state is always reproducible)
tests/                               Playwright checks; `node tests/<name>.js`; screenshots land in tests/out/
reference/                           Ruby's sketches, the four versions of the Canon art, Joshua's original spin page, v10 screenshots
```

## Build, test, ship

```
pip install -r requirements.txt            # numpy, opencv-python-headless, Pillow (Python 3.11 used)
npm install && npx playwright install chromium

make maps      # cd pipeline && python3 mapgen2.py     (~15 s; deterministic, fixed seeds)
make check     # cd pipeline && python3 check_edges.py  (prints per-edge agreement, writes edge_check.png)
make build     # python3 pipeline/build.py  -> dist/tetra.html (fragment) and dist/tetra_world.html (standalone)
make test      # smoke, walkthrough, phases, tap  (all must exit 0)
make seams     # six seam screenshots in tests/out/seam_*.png: look at them after any map change
make audit     # em dashes, retired names, placeholders: must print 'audit clean'
```

Verified on 2026-10-02: from a clean copy of this repo, `make maps && make build` reproduces `dist/` byte for byte, and `make test` passes.

**Shipping.** `dist/tetra.html` is the body fragment the claude.ai artifact is published from; `dist/tetra_world.html` is the same thing wrapped in a full document and is what Joshua sends to Ruby. Claude Code has no tool to republish the artifact; to update the live link, hand `dist/tetra.html` to a Claude conversation and have it publish to the URL above (version labels so far: "v10 Ruby's fixes, purple star, rings"). Otherwise, deliver `dist/tetra_world.html` directly; it is self-contained (about 1.9 MB, all textures inlined as base64).

## Geometry conventions (read before touching maps or edges)

- Vertices: `V0` apex (Spikia, the shared "spike" corner), `V1`, `V2` the front base corners, `V3` the back corner (the Wetia corner, where all three deltas meet).
- Faces and their vertex order (`FACES` in template, `FACE_IDX` in edges.py): `canon (0,1,2)`, `west (0,3,1)`, `south (0,2,3)`, `far (1,3,2)`. The order is (apex, bottom-left, bottom-right) of that face's texture.
- Texture space is 1024x1024, apex-up: `APEX (512, 75.52)`, `BL (8, 948.48)`, `BR (1016, 948.48)` (`APEX_UP` in mapgen.py). The Far face is drawn with `FACE_VIEW_YAW far = -pi/3` so it reads apex-up when flown to.
- Edges are keyed by sorted vertex pair, `t` runs from the lower id to the higher. Which local edge is which:
  - West: left = `0-3` (shared with South), right = `0-1` (Canon), bottom = `1-3` (Far).
  - South: left = `0-2` (Canon), right = `0-3` (West), bottom = `2-3` (Far).
  - Far: left = `1-3` (West), right = `1-2` (Canon), bottom = `2-3` (South).
- The Canon face is Ruby's painting, so its three edges (`0-1`, `0-2`, `1-2`) are **measured** from `tex_canon.jpg` (`edges.measure_canon`, water classifier `(b>r+30)&(b>95)&(g>r+8)`). The other three are **designed** in `edges.profiles()` as water intervals of t: `0-3` water (0.40, 0.60); `1-3` water (0.28, 0.75); `2-3` water (0.10, 0.30) and (0.54, 0.80). Change them there, delete `edge_profiles.json`, regenerate.
- `edges.conform(land, face)` blends a face's land mask toward the profiles in a tapered, noisy band along each edge so coasts continue across edges without rectangular tabs (the "blocky stuff" Ruby complained about once).

## Pipeline (what reads and writes what)

1. `bake.py` (only when the Canon art changes): `art_latest.png` -> `tex_canon.jpg`, `geometry.json` (layouts + the Canon regions as barycentric coords). The kite A,P,D,Q in the art is the Canon face; the art's own West/South region names (Sunreach, Evermere, etc.) are NOT canon and are cropped away.
2. `blobs.py`: Ruby's continent and central-island outlines, hand-typed from her sketches, scaled and fitted inside the triangle. Imported by mapgen2.
3. `mapgen2.py`: `design_west / design_south / design_far` build a land mask from masses (`supergauss`, `wobble`, `band`, `wedge`, `moat`), run `conform`, turn it into heights (`heights`), assert water >= 0.5 and markers on land (`check_markers`), paint it (`paintface.render_painted`, which harvests patches from `art_latest.png` through `texsynth`), then write `map_*.jpg` (clean, for the world), `codex_*.jpg` (labelled, for the Codex), `codex_island.jpg` / `codex_continent.jpg` (nation close-ups), `map_*_prev.png` (markers drawn, for eyeballing), `map_anchors.json`, `water_fractions.json`. Marker positions are the `P` dicts in each design; island/continent nations are offsets in `nations.py`.
4. `check_edges.py`: samples both sides of each edge at depths 14..30 px and reports agreement. Current: 0-1 100%, 0-2 96.3%, 0-3 97.0%, 1-2 98.3%, 1-3 96.7%, 2-3 97.7%.
5. `build.py`: merges `names` (marker display names for anchors), `nations.py` offsets and `geometry.json` into the GEOMETRY JSON, base64-inlines the textures, writes `dist/`. **If you add a place to a map, add its display name to `names` in build.py and its card to `WORLD.places` in the template.**
6. `west_places.json`, `south_far_places.json`: inputs of the old `mapgen.py` main (superseded). `mapgen2.py` hard-codes its positions instead.

## template.html, where things are

Single file: `<style>` (lines ~4-234), HTML (~236-348: canvas `#gl`, `#markers`, the Codex `#codex` with tabs `tabWorld / tabRegions / tabPlace`, the HUD with `#rngDay`, `#btnPlay`, the four `[data-face]` buttons), `<script>` (~349-740). Find things by grepping for these anchors rather than by line number:

- `const WORLD = {` : all content. `calendar` (13 months x 28 days + 1 Restart Day = 365; seasons), `places` (one card per marker id: name, kind, nation, biome, note, chart), `nations` (grouped list for the World tab), `explorers`, `worlds` (Tetra, The Inverted Planet), `star`, `fields`, `faces` (name, tagline, blurb, note, color), `lore` (draft prose per Canon region).
- `LABEL_SIDE` : which side a marker's label sits on (`left` / `below`), to stop overlaps.
- `const V =` / `const FACES =` : the tetrahedron. `GEO` is the injected geometry JSON (regions with barycentric `b`).
- `sunDir(day)` : sun direction; `SUN0`, `TILT`, `SUMMER_MID` give the seasons their elevation. `rainAmount(day)` drives rain on the Canon face in rain season.
- Shader `FS` : uniforms `uSun, uTime, uSpinDir, uAmbient, uHighlight, uSunColor, uFar`. `uFar` clamps `nl` to [-0.21, 0.34] on the Far face (Ruby: "the far side does not have high sun, or deep night").
- `phaseFor(r, sun)` -> `phaseOf(nl, toward)` : the phase text on cards. Mount Celestial (`celestial`) is pinned to "Twilight, always"; Far-face regions get the same clamp as the shader. Thresholds: High sun >= 0.72, Morning/Afternoon >= 0.35, The slow morning/Late light >= 0.05, First light/Dusk >= -0.22, Before dawn/Evening >= -0.55, else Deep night.
- `drawStars` : the sky, the star's glow (dark purple since v10), the anti-sun blue glow. `ringPoints` (alias `arcPoints`) : the gold (magical) and blue (magnetic) field rings, full circles since v10, 3 of each. `drawOverlay` strokes them and runs the particles.
- `selectFace(id, fly)` / `selectRegion(id)` / `openCodex(on)` : navigation. `if(!fly||W>=820)openCodex(true)` is what makes a tap on the world open the Codex on phones.
- `window.tetra = {state, setDay, select, face, release, phase}` : debug hook used by the tests. `phase(id)` returns the phase object a card would show for the current `state.day`.
- The World tab has a "World file" group with the JSON export (`worldJson()`), and lore edits are saved to `localStorage` per browser ("Edit lore" on a card).

Copy style inside the page: small caps eyebrows, Lora italics for the explorers' voice, no em dashes, British-flavoured spellings already in use ("colour", "centre"). Keep it.

## Testing notes

- Playwright 1.56, Chromium. Headless WebGL needs the swiftshader flags in `tests/_page.js`; on a machine with a GPU they are harmless.
- `tests/walkthrough.js` prints the card text it saw; read it, the content matters as much as the absence of errors.
- `tests/phases.js` sweeps a year through `window.tetra.phase`; it fails if any Far-face place reaches High sun or Deep night, if Mount Celestial is ever not twilight, or if the Canon face loses either.
- `tests/tap.js` performs a real touch tap at phone width and fails if the Codex stays closed.
- `tests/archive/` holds the ad hoc scripts from earlier rounds (older ids may no longer exist; they are kept for the recipes, not as a suite).
- For map changes also look at `pipeline/map_*_prev.png` (markers), `tests/out/seam_*.png` (edges), and `edge_check.png`.

## How a round from Ruby is processed

1. Transcribe her messages verbatim into `HANDOFF.md` (ledger), one line per instruction, with the date.
2. Decide the literal reading of each line; note any reading that had to be chosen.
3. Maps: edit the design in `mapgen2.py` (masses, `P` positions, `LABELS`), `nations.py` (nation offsets), `edges.py` (designed intervals; delete `edge_profiles.json`). `make maps && make check`. Look at the previews and the water fractions.
4. Page: edit `WORLD` in `template.html` (places, nations, faces, explorers, lore) and `names` in `build.py`. Marker ids must exist in `map_anchors.json` (or in `geometry.json` for the Canon face).
5. `make build && make test && make seams && make audit`, look at every screenshot.
6. Ship both files. Report back in Ruby's terms: what each of her lines turned into, and which lines needed a guess.
