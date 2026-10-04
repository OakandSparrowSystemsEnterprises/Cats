# Cuba (The Dice System)

Cuba is Ruby's cube planet, the second world of The Dice System after Tetra. Read `../tetra/CLAUDE.md` first: its ground rules are the rules here too (canon comes from Ruby by chat, relayed by Joshua; never invent canon, mark every reading as a reading; no em dashes anywhere, `make audit` fails on them; test before shipping; Ruby's spellings exactly). Then read `HANDOFF.md` here (state, the canon ledger, the open questions). Joshua is the client; Ruby is the author.

## What exists (draft 3, 2026-10-04)

Cuba is a second world inside Tetra's page (Ruby: "it neends to be in the same file as tetra"): `../tetra/pipeline/template.html` carries a Tetra/Cuba switch under the title (`#diceWorlds`, remembered in `localStorage` as `dice.world`) and inserts Cuba's fragment at `{{CUBA}}`. The world not shown sleeps (class `away`: hidden, its frame loop idle). Cuba shares Tetra's dark purple star (the same direction `SUN0`, drawn a little smaller: it is farther out).

A WebGL cube with six square sides, turning leftward once a day like Tetra, with Tetra's star and two field rings (gold magical, blue magnetic, a little stronger than Tetra's). Only the Canon side is drawn: the Plus Continent (Ruby's name for her central island, a broad cross with rounded bends at the corners) whose four arms reach the sides and connect onto the East, West, North and South sides (her words), with the Canyon in its middle, the small hole that takes you through the world to the Far side. On those four sides the land continues a short way (`TONGUE`, a reading) and the rest is uncharted slate; the Far side carries the hole's other end and nothing else. A Codex panel holds the World tab (her words and the readings), the six sides and a card per side or place. Tetra's mechanics carried over (Ruby: "transfer core mecanics from tetra to cuba"): `state.day` with the spin and day sliders, Pause and Reset, the HUD date on Cuba's calendar (14 months of 28 days, Amberary the fourteenth between Tredesember and March, the Restart Day of 1.25 days closing the 393.25-day year; `dateParts`, `seasonFor` with Amberary's two halves, `rainAmount`, the strip `renderYear` from March, no year number), the d5 moon (`moonMesh`, `moonState`, `moonModel`, `prog2`: a prism along the orbit axis, one to five craters a side, phases over the month, the eased swing and eclipse on the 14th), the phase words (`placeLight`, `phaseOf`, `phaseFor`) on cards and in the Sides list, Follow this side and Release view (`setFollow`, `camYaw`), rain over the Canon side (`drawRain`), the field rings (`drawFields`). The star is drawn only where it is (`lastStar`, no edge clamp: Ruby, "the sun moves because it refuses to go of the frame, remove this").

The Plus Continent is drawn from a written description of Ruby's photo, not from the photo itself (it had not reached the repository): Ruby's original photographed drawing, visually transcribed by ChatGPT, with the arm connections subsequently confirmed by Ruby. The shape is to be checked against the photo when it arrives (`reference/ruby/README.md`). How far the arms run onto the four neighbouring sides is provisional (`TONGUE`).

## Layout

```
CLAUDE.md, HANDOFF.md, Makefile
pipeline/
  mapgen.py          the face textures: map_canon.jpg (the island and the hole), map_east/west/north/south.jpg (the island's arm continuing onto that side, `TONGUE`, then uncharted slate), map_far.jpg (the hole's other end), map_blank.jpg (uncharted), anchors.json (marker positions), map_canon_prev.png (markers drawn)
  world.html         Cuba's fragment for Tetra's page: <style> scoped under #capp, <div id="capp" class="away">, <script>; placeholders {{CUBA_TEX_CANON}}, {{CUBA_TEX_EAST}}, {{CUBA_TEX_WEST}}, {{CUBA_TEX_NORTH}}, {{CUBA_TEX_SOUTH}}, {{CUBA_TEX_FAR}}, {{CUBA_TEX_BLANK}}, {{CUBA_ANCHORS}}. Every element id starts with c (cgl, ccodex, ctabWorld, cplaceBody, cfaceButtons ...) so nothing collides with Tetra's.
tools/audit.py       em dashes in Cuba's files (the built page is audited in ../tetra)
reference/ruby/      Ruby's pictures for Cuba (none received yet)
The build, the tests (../tetra/tests/cuba.js) and the shipped files live in ../tetra.
```

## Build, test, ship

```
make maps      # here: cd pipeline && python3 mapgen.py   (deterministic, asserts: one piece of land, arms reaching the middle of each side, corners water, the hole in the middle, the land agreeing across the four edges)
make audit     # here: em dashes in Cuba's files
cd ../tetra && make build && make test && make audit     # the page: tests/cuba.js switches to Cuba and checks the six sides in Ruby's arrangement, the island and hole pixels, the star's glow, the Far side, the phone Codex, and the switch back to Tetra
```

Python 3.11 with numpy, OpenCV (`opencv-python-headless<5`) and Pillow from `../tetra/requirements.txt`. Ship Tetra's two files, which carry Cuba: `../tetra/dist/tetra.html` (republished to Tetra's artifact) and `../tetra/dist/tetra_world.html`.

## Geometry conventions

- Cube of half-size 1 at the origin, spinning about the North-South axis (Y). `FACES` in the template: `canon` +Z, `far` -Z, `west` +X, `east` -X, `north` +Y (top), `south` -Y (bottom). Each face has a `right` and an `up` vector; texture row 0 is the top of the face, column 0 its left.
- Ruby's arrangement (her net: East, Canon, West, Far in a row, North above Canon, South below): looking at Canon with North up, East is on the LEFT and West on the RIGHT, Far behind. So `east` is -X and `west` is +X. Keep it; it is hers. North's `up` points toward Far, South's `up` toward Canon, as the net unfolds.
- Face textures are 1024 x 1024 px. The tongue texture is drawn once with the land at the top edge and rotated per side (East: right edge, West: left, North: bottom, South: top, the edges each shares with Canon). `anchors.json` holds marker positions in face px per side. `facePoint(side, px, py)` in the template maps them onto the cube.
- Cuba turns leftward once a day like Tetra (`state.spin -= dt*speed*TAU/DAY_SECONDS`, `DAY_SECONDS` 30 as in Tetra; Ruby 2026-10-04: "same as tetra").

## world.html, where things are

`WORLD` (sides, places, lore: her words verbatim), `FACES`, `SUN0` and `STAR_SIZE` (Tetra's star direction, the glow drawn in `drawStars` as on Tetra, at the edge toward the star when it is out of view), `ringPoints`/`strokeRing`/`drawFields` (the two fields on the `cfx` overlay canvas, occluded by the world taken as a ball of radius 1.62), the shaders `VS`/`FS` (lit from `SUN0`), `buildMarkers`/`updateMarkers`, the Codex (`showTab`, `openCodex`, `renderSides`, `renderPlace`, `selectSide`, `selectPlace`), the dock (six face buttons from `WORLD.sides`, Codex, Pause/Spin, Reset), pointer handling (drag turns, wheel zooms, a tap on the world selects the facing side), the frame loop, and the debug hook `window.cuba = {state, face(id, fly), facing(), neighbours(), markers(), sample(id), sampleAt(fx, fy), starPixel(), setSpin(on), select(id)}` used by the tests (`sample` reads the drawn pixel under a marker, `starPixel` the sky pixel at the star's glow). `window.dice = {ready(key, fn), snapshot(key, fn), boot(), show(id), world}` is the page's bridge (in the Tetra template): both worlds register their start and snapshot functions with it, and one hot-reload hook starts both from one snapshot (each used to register its own, and only one survived, so Tetra came up blank after a republish). The hook adds `setDay`, `setYaw`, `date()`, `moon()`, `phase(id)`, `follow`, `release`, `starScreen()`, `sunDir()`. `neighbours()` reports which side is left, right, up, down and behind the facing side on screen. Hot reload (`window.claude.hot`) restores spin, camera and play state, as Tetra does.

## How a round from Ruby is processed

As for Tetra (`../tetra/CLAUDE.md`, last section): her words verbatim into `HANDOFF.md` first, the literal reading noted, then maps (`mapgen.py`, `make maps` here), page (`WORLD` and the World tab in `world.html`), then in `../tetra`: `make build && make test && make audit`, look at `tests/out/cuba_*.png` there and `pipeline/map_canon_prev.png` here, ship Tetra's two files, report in her terms.
