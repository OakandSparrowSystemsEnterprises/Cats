# Tetra (The Dice System)

Tetra is a four-sided world: an interactive WebGL tetrahedron, one map per face, a day/night cycle, a 13-month calendar and a "Codex" side panel of places, nations and lore. It is Ruby's world (Joshua's child). **Canon comes from Ruby, by chat, relayed by Joshua. Nothing here is invented beyond what she has said; where the build had to guess, the guess is marked as a guess in the Codex ("Still unwritten", "not yet written").** Joshua is the client; Ruby is the author.

Shipped state: **version 11** (2026-10-03). `dist/tetra_world.html` is the single-file build of that version. The published copy lives at `https://claude.ai/artifact/G6JjTxacMzAGCtcSrETb8v` (private artifact, republished from `dist/tetra.html`, see "Shipping" below). Read `HANDOFF.md` for the state, the change ledger and the open questions.

## Ground rules (Joshua's, and they are firm)

1. **Never invent canon.** Ruby's words are the source. If a request is ambiguous, implement the most literal reading and say which reading was taken. Draft lore (`WORLD.lore` in the template) is first-pass text for Joshua to edit, and it is labelled as such in the page.
2. **No em dashes anywhere** in copy, code comments, docs or commit messages. Use commas, periods, parentheses, or restructure. `make audit` (tools/audit.py) fails on any em dash in every text file of the repo (pipeline scripts and legacy scripts, template, tests and archived tests, tools, the docs, Makefile and manifests, and `dist/` with the base64 stripped), on retired names in the files that feed the shipped page (`template.html`, `build.py`, `nations.py`, `mapgen2.py`, `tests/`, `dist/`), and on unreplaced `{{...}}` placeholders in `dist/`.
3. **Test before shipping. Every time.** Joshua is not the test bed. Minimum: `npm test` passes (no script or console errors at 1366 px and 393 px, Far-face phase rules hold, phone tap opens the Codex), plus eyeball the screenshots in `tests/out/` and the six seam screenshots from `npm run seams` (`tests/out/seam_*.png`) after any map change.
4. **Every face is at least half water** (`mapgen2.py` asserts it) and **every marker sits on land** (asserted too). Landmasses line up across every edge (`check_edges.py`; v11 ships with the worst edge at 3.3% disagreement, so treat anything above about 5% as a regression).
5. **Use Ruby's outlines, not the explorers' pictures.** In-world, the explorers Sapphire, Amethyst and Obsidian made rough charts and Opal "went back and made complete maps". The page shows Opal's maps (generated from the sketches), never the sketch photos. Since v11 the Canon face is generated too, from the outline and the places of Ruby's painting, rather than shown as the painting itself (Ruby, 2026-10-03: no land on the west and east sides, no clouds, at least half water, the same look as the other sides). The Canon map is not attributed to Opal in the page; Ruby never said who charted it.
6. Names are spelled exactly as Ruby spells them (`It's Hot` is the nation's full name; `Marshia`, `Baiuland`, `Greeneria`, `Wetia`, `Tredesember`; `Ughia`, which was read as Uohia until 2026-10-03).
7. Deliverables each round: the republished artifact (same URL) **and** the standalone `dist/tetra_world.html`.

## Repo layout

```
CLAUDE.md, HANDOFF.md, README.md      this file, the state/ledger, the quickstart
Makefile, package.json, requirements.txt
pipeline/                            everything that makes the page; scripts run with cwd = pipeline/
  template.html                      the whole app (CSS + HTML + JS) with {{PLACEHOLDERS}} for textures and geometry
  build.py                           inlines textures/geometry into template.html -> dist/tetra.html + dist/tetra_world.html
  mapgen2.py                         CURRENT map designer for all four faces (writes map_*.jpg, codex_*.jpg, map_anchors.json, water_fractions.json)
  mapgen.py                          helpers (noise, masks, labels, rivers, Codex crops) + the first-pass designer (superseded)
  edges.py                           shared-edge land/water profiles and conform(); caches to edge_profiles.json
  paintface.py                       turns a height design into painted terrain (land layer + sea layer, cut on the coastline)
  texsynth.py                        patch-quilting texture synthesis from the Canon art (art_latest.png)
  blobs.py                           Ruby's outlines (continent, central island) typed in by hand, in texture space
  nations.py                         where the island / continent nations sit (shared by mapgen2 and build)
  bake.py, radial.py                 Canon face: warps Ruby's painting (art_latest.png) into tex_canon.jpg + geometry.json (also writes tex_west/south/far.jpg, unused placeholders, gitignored)
  check_edges.py                     measures land/water agreement along the six edges -> edge_check.png
  art_latest.png                     Ruby's Canon painting (1448x1086). Source of the Canon OUTLINE and of all terrain patches
  tex_canon.jpg, geometry.json       outputs of bake.py: the painting warped into the triangle (since v11 only the source of the Canon outline and of the measured bottom edge, not shown), face layouts, Canon region positions as measured on the painting
  map_{canon,west,south,far}.jpg     outputs of mapgen2.py: the face textures (no labels; labels are HTML markers)
  codex_{canon,west,south,far,island,continent}.jpg   labelled Codex charts (Opal's maps)
  map_anchors.json                   marker positions in texture px per face (mapgen2 -> build)
  edge_profiles.json                 CACHE of edge profiles. Delete it after changing tex_canon.jpg or the designed intervals
  blobs.json, water_fractions.json, west_places.json, south_far_places.json   small data files (see "Pipeline"; blobs.json is an export written by `python3 blobs.py`, nothing reads it)
  zinnia_q.png                       the Umbrella Tree Zinnia cutout shown in the Codex
  fonts/Lora-*.ttf                   label fonts for the Codex charts (OFL)
  legacy/                            sketch-processing scripts from earlier rounds (not in the build path)
dist/                                build outputs (committed so the shipped state is always reproducible)
tests/                               Playwright checks; `node tests/<name>.js`; screenshots land in tests/out/
tools/                               audit.py, what `make audit` runs
reference/                           Ruby's sketches, the four versions of the Canon art, Joshua's original spin page, v10 screenshots
```

## Build, test, ship

```
pip install -r requirements.txt            # numpy, opencv-python-headless, Pillow (Python 3.11 used)
npm install && npx playwright install chromium

make maps      # cd pipeline && python3 mapgen2.py     (~15 s; deterministic, fixed seeds)
make check     # cd pipeline && python3 check_edges.py  (prints per-edge agreement, writes edge_check.png)
make build     # python3 pipeline/build.py  -> dist/tetra.html (fragment) and dist/tetra_world.html (standalone)
make test      # rebuilds dist/ first, then smoke, walkthrough, phases, tap  (all must exit 0)
make seams     # rebuilds dist/ first, then six seam screenshots in tests/out/seam_*.png: look at them after any map change
make audit     # em dashes, retired names, placeholders: must print 'audit clean'
```

Verified on 2026-10-02: from a clean copy of this repo, `make maps && make build` reproduces `dist/` byte for byte, and `make test` passes.

Verified again the same day from the repository checkout (Claude Code; Python 3.11, numpy 2.4, OpenCV 4.14, Playwright 1.56, Chromium 141) with the same result. OpenCV 5.x writes slightly different JPEG bytes (the maps are pixel-identical within JPEG noise, anchors and fractions identical), so `requirements.txt` pins `opencv-python-headless<5`.

**Shipping.** `dist/tetra.html` is the body fragment the claude.ai artifact is published from; `dist/tetra_world.html` is the same thing wrapped in a full document and is what Joshua sends to Ruby. A Claude Code session that has the Artifact tool can republish the live link itself: read the URL above first (action read), then publish `dist/tetra.html` to it (action publish with that url and a short label), as was done for v11 on 2026-10-03. Without that tool, hand `dist/tetra.html` to a Claude conversation and have it publish to the URL. Version labels so far: "v10 Ruby's fixes, purple star, rings", "v11 Canon as a map, Tree Land joined, d3 moon, years". Either way also deliver `dist/tetra_world.html`; it is self-contained (about 1.6 MB, all textures inlined as base64).

## Geometry conventions (read before touching maps or edges)

- Vertices: `V0` apex (Spikia, the shared "spike" corner), `V1`, `V2` the front base corners, `V3` the back corner (the Wetia corner, where all three deltas meet).
- Faces and their vertex order (`FACES` in template, `FACE_IDX` in edges.py): `canon (0,1,2)`, `west (0,3,1)`, `south (0,2,3)`, `far (1,3,2)`. The order is (apex, bottom-left, bottom-right) of that face's texture.
- Texture space is 1024x1024, apex-up: `APEX (512, 75.52)`, `BL (8, 948.48)`, `BR (1016, 948.48)` (`APEX_UP` in mapgen.py). The Far face is drawn with `FACE_VIEW_YAW far = -pi/3` so it reads apex-up when flown to.
- Edges are keyed by sorted vertex pair, `t` runs from the lower id to the higher. Which local edge is which:
  - West: left = `0-3` (shared with South), right = `0-1` (Canon), bottom = `1-3` (Far).
  - South: left = `0-2` (Canon), right = `0-3` (West), bottom = `2-3` (Far).
  - Far: left = `1-3` (West), right = `1-2` (Canon), bottom = `2-3` (South).
- Canon: left = `0-1` (West), right = `0-2` (South), bottom = `1-2` (Far).
- The Canon bottom edge `1-2` is **measured** from `tex_canon.jpg`, Ruby's painting (`edges.measure_canon`, water classifier `(b>r+30)&(b>95)&(g>r+8)`); the Far face follows it. The five other edges are **designed** in `edges.profiles()` as water intervals of t: `0-1` and `0-2` water (`SPIKE_T` = 0.25, `CORNER_T` = 0.93): open sea below Spikia on both Canon sides down to the bottom corners, which stay land because the bottom edge is the painted coast (Ruby, 2026-10-03; the corner reading is recorded in HANDOFF.md); `0-3` water (0.40, 0.60); `1-3` water (0.28, 0.75); `2-3` water (0.10, 0.30) and (0.54, 0.80). Change them there, delete `edge_profiles.json`, regenerate.
- `edges.conform(land, face)` blends a face's land mask toward the profiles in a tapered, noisy band along each edge so coasts continue across edges without rectangular tabs (the "blocky stuff" Ruby complained about once).

## Pipeline (what reads and writes what)

1. `bake.py` (only when the Canon art changes): `art_latest.png` -> `tex_canon.jpg`, `geometry.json` (layouts + the Canon regions as barycentric coords). The kite A,P,D,Q in the art is the Canon face; the art's own West/South region names (Sunreach, Evermere, etc.) are NOT canon and are cropped away. `bake.py` hard-codes, in art pixels, the kite A,P,D,Q, the radial warp centre `ck` and the 13 Canon region positions in `regions`; a new painting needs all of them re-measured (the barycentric assert only catches a region that lands outside the triangle). It also writes `tex_west/south/far.jpg`, placeholder stone from before mapgen2 that nothing reads; they are gitignored.
2. `blobs.py`: Ruby's continent and central-island outlines, hand-typed from her sketches, scaled and fitted inside the triangle. Imported by mapgen2.
2b. `mapgen2.design_canon`: the Canon face. `canon_outline` reads the painting (`tex_canon.jpg`) as land wherever it is neither sea (blue classifier) nor cloud (bright, unsaturated; a cloud pixel takes the class of the nearest clear pixel) and simplifies the coast. `canon_pieces` cuts it into the painting's landmasses by region group (`CANON_GROUPS`: egg, chicken, islandia, south, spike), splitting a shared landmass along the line of equal distance to the groups' markers. `place` scales each island about its centroid (`ISLAND_SCALE`, shrinking a notch at a time until `CHANNEL` px of water separate every pair) and slides it clear of the side sea (`SIDE_CLEAR`); the southern land is `dome`, a half-disc on the middle of the bottom edge (`DOME_A` wide, as tall as half water and the channel allow); Spikia is `wedge(290)` as on the other faces. `canon_positions` converts the 13 regions' barycentrics from `geometry.json` to px; island regions move with their island; `settle` moves any marker left in the water, or closer than 16 px to the coast, onto the nearest land 16 px inland (printed when it happens; a move over 60 px fails the run, because then a person should place it). Zones come from distance to the region markers (white at Whiteland, gold at Yolkia and Llamaland, forest at Islandia, Unoooland, Ughia and the Feathers, green at Neckia, Rainia and Footia, redrock at the Headlands and It's Hot).
3. `mapgen2.py`: `design_canon / design_west / design_south / design_far` build a land mask from masses (`supergauss`, `wobble`, `band`, `wedge`, `moat`), run `conform`, turn it into heights (`heights`), assert water >= 0.5 and markers on land at least 14 px from the coast (`check_markers`), paint it (`paintface.render_painted`, which harvests patches from `art_latest.png` through `texsynth`), then write `map_*.jpg` (clean, for the world), `codex_*.jpg` (labelled, for the Codex), `codex_island.jpg` / `codex_continent.jpg` (nation close-ups), `map_*_prev.png` (markers drawn, for eyeballing), `map_anchors.json`, `water_fractions.json`. Marker positions are the `P` dicts in each design; island/continent nations are offsets in `nations.py`.
4. `check_edges.py`: samples both sides of each edge at depths 14..30 px and reports agreement. Current (v11): 0-1 99.7%, 0-2 99.3%, 0-3 97.0%, 1-2 100%, 1-3 96.7%, 2-3 97.7%.
5. `build.py`: merges `names` (marker display names for anchors), `nations.py` offsets and the Canon regions (names and order from `geometry.json`, positions from `map_anchors.json['canon']`) into the GEOMETRY JSON, base64-inlines the textures (`map_canon.jpg` is the Canon texture since v11) and the Codex charts, writes `dist/`. **If you add a place to a map, add its display name to `names` in build.py (or to `geometry.json` for the Canon face) and its card to `WORLD.places` in the template.**
6. `west_places.json`, `south_far_places.json`: inputs of the old `mapgen.py` main (superseded). `mapgen2.py` hard-codes its positions instead (except `continent-south`, the centroid of the continent polygon, and `celestial`, the face centre). **Never run `python3 mapgen.py` directly:** its main still writes `map_*.jpg`, `codex_*.jpg`, `map_*_prev.png` and `map_anchors.json` and would overwrite the current maps with the superseded design and its retired labels, which `make audit` cannot see inside a JPEG. `make maps` (mapgen2.py) is the only generator; if it happens, `git checkout -- pipeline/` restores the shipped maps.

## template.html, where things are

Single file: `<style>` (lines ~4-234), HTML (~236-348: canvas `#gl`, `#markers`, the Codex `#codex` with tabs `tabWorld / tabRegions / tabPlace`, the HUD with `#rngDay`, `#btnPlay`, the four `[data-face]` buttons), `<script>` (~349-740). Find things by grepping for these anchors rather than by line number:

- `const WORLD = {` : all content. `calendar` (13 months x 28 days + 1 Restart Day = 365; seasons), `places` (one card per marker id: name, kind, nation, biome, note, chart), `nations` (grouped list for the World tab), `explorers`, `worlds` (Tetra, The Inverted Planet), `star`, `moon` (the d3), `years` (year 0 and -0, `now` = 1700, the HUD's `YEAR0`), `timeline` (Ruby's key events from her comics: year, `said` = her words, `shows`), `fields`, `faces` (name, tagline, blurb, note, color, chart), `lore` (draft prose for the eight Canon regions from the painting; the four kingdoms and Spikia have none yet and show "Nothing written yet").
- `LABEL_SIDE` : which side a marker's label sits on (`left` / `below`), to stop overlaps.
- `const V =` / `const FACES =` : the tetrahedron. `GEO` is the injected geometry JSON (regions with barycentric `b`).
- `dateParts(day)` : the HUD date; `YEAR0 = WORLD.years.now` is the year the first day is in (1700).
- `sunDir(day)` : sun direction; `SUN0`, `TILT`, `SUMMER_MID` give the seasons their elevation. `rainAmount(day)` drives rain on the Canon face in rain season.
- Shader `FS` : uniforms `uSun, uTime, uSpinDir, uAmbient, uHighlight, uSunColor, uFar`. `uFar` clamps `nl` to [-0.21, 0.34] on the Far face (Ruby: "the far side does not have high sun, or deep night").
- `phaseFor(r, sun)` -> `phaseOf(nl, toward)` : the phase text on cards. Mount Celestial (`celestial`) is pinned to "Twilight, always"; Far-face regions get the same clamp as the shader. Thresholds: High sun >= 0.72, Morning/Afternoon >= 0.35, The slow morning/Late light >= 0.05, First light/Dusk >= -0.22, Before dawn/Evening >= -0.55, else Deep night.
- `drawStars` : the sky, the star's glow (dark purple since v10), the anti-sun blue glow, then `drawMoon`: the d3 moon (`moonSpot` places it `MOON_SPOT` radians round from the star at a stand-in size `MOON_SIZE`; hidden when behind the world or off screen). `ringPoints` (alias `arcPoints`) : the gold (magical) and blue (magnetic) field rings, full circles since v10, 3 of each. `drawOverlay` strokes them and runs the particles.
- `selectFace(id, fly)` / `selectRegion(id)` / `openCodex(on)` : navigation. `if(!fly||W>=820)openCodex(true)` is what makes a tap on the world open the Codex on phones.
- `window.tetra = {moon, state, setDay, select, face, release, phase}` : debug hook used by the tests. `phase(id)` returns the phase object a card would show for the current `state.day`; `moon(spot)` returns the moon's screen position (or null) for the current day, optionally for another angle.
- The Regions tab ends with a "World file" group holding the JSON export (`worldJson()`, inserted after `#reggroups` at runtime; the page's own "Copy the world JSON" note points there). Lore edits are saved to `localStorage` per browser ("Edit lore" on a card).

Copy style inside the page: small caps eyebrows in Cinzel (`var(--display)`), Cormorant Garamond italics (`var(--serif)`: `.tagline`, `.q`) for the explorers' voice, IBM Plex Sans (`var(--ui)`) for the chrome, all three from Google Fonts; no em dashes; British-flavoured spellings already in use ("colour", "centre"). Keep it. Lora is not used by the page at all; it is only the label font that `mapgen.label()` bakes into the Codex chart JPEGs.

## Testing notes

- Playwright 1.56, Chromium. Headless WebGL needs the swiftshader flags in `tests/_page.js`; on a machine with a GPU they are harmless.
- `tests/walkthrough.js` prints the card text it saw; read it, the content matters as much as the absence of errors. Its "phone codex open after face tap?" line is informational only (it prints the panel transform and goes through the face-button path); `tests/tap.js` is the real phone tap check.
- The World tab is static HTML in `#paneWorld` (sections: the world, the calendar, the two fields, the star, the moon, the four faces, the Dice System, Life of Tetra, Nations, Explorers, Key events, Still unwritten) plus lists filled from `WORLD` at startup (`#facelist`, `#worlds`, `#nations`, `#explorers`, `#timeline`).
- `tests/phases.js` sweeps a year (every 7th day, every half hour) through `window.tetra.phase` for a fixed list of ids; it fails if any of the five Far-face places it knows (`warmia`, `ehia`, `treeland`, `delta-far`, `mountains-far`) reaches anything other than First light, The slow morning, Late light or Dusk (High sun, Morning, Afternoon, Evening, Before dawn and Deep night all fail it), if Mount Celestial is ever not twilight, or if the Canon face loses High sun or Deep night. Add any new Far-face id to that list.
- `tests/tap.js` performs a real touch tap at phone width and fails if the Codex stays closed.
- `tests/archive/` holds the ad hoc scripts from earlier rounds (older ids may no longer exist; they are kept for the recipes, not as a suite).
- For map changes also look at `pipeline/map_*_prev.png` (markers), `tests/out/seam_*.png` (edges), and `edge_check.png`.
- The page's only external fetch is the Google Fonts stylesheet (Cinzel, Cormorant Garamond, IBM Plex Sans). Offline or behind a proxy it fails, the page falls back to system fonts, and `PAGE.isNetworkError` in `tests/_page.js` keeps that `net::ERR_*` console line out of the error count. Screenshots taken offline show the fallback fonts.

## How a round from Ruby is processed

1. Transcribe her messages verbatim into `HANDOFF.md` (ledger), one line per instruction, with the date.
2. Decide the literal reading of each line; note any reading that had to be chosen.
3. Maps: edit the design in `mapgen2.py` (masses, `P` positions, `LABELS`), `nations.py` (nation offsets), `edges.py` (designed intervals; delete `edge_profiles.json`). `make maps && make check`. Look at the previews and the water fractions.
4. Page: edit `WORLD` in `template.html` (places, nations, faces, explorers, lore) and `names` in `build.py`. Marker ids must exist in `map_anchors.json` (or in `geometry.json` for the Canon face).
5. `make build && make test && make seams && make audit`, look at every screenshot.
6. Ship both files. Report back in Ruby's terms: what each of her lines turned into, and which lines needed a guess.
