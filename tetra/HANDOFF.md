# Handoff: Tetra, version 10 (2026-10-02)

Written for the next Claude Code session picking this up from the Claude app conversation where versions 1 through 10 were built. Read `CLAUDE.md` first for the rules and the layout; this file is the state.

## 1. What is shipped

- Published artifact: `https://claude.ai/artifact/G6JjTxacMzAGCtcSrETb8v`, **version 10**, label "v10 Ruby's fixes, purple star, rings", published 2026-10-01 from `dist/tetra.html`.
- Standalone copy sent to Joshua the same day: `dist/tetra_world.html` (identical content, wrapped in a full HTML document).
- Both files in `dist/` are byte-identical to what was published (verified by rebuilding from a clean copy of this repo on 2026-10-02: `make maps && make build` reproduces them, `make test` passes). Re-verified from the repository checkout the same day, see section 9.
- Screenshots of v10 are in `reference/screenshots-v10/` (desktop home, each face, the Mount Celestial card, the World tab, phone views, the six-seam sheet).

## 2. What the page does

A tetrahedron (four equilateral faces) spins leftward once per world day under a dark purple star. The Canon face carries Ruby's painting; West, South and Far carry generated maps in the same painted style. HTML markers sit on the faces; tapping a marker or a face opens the Codex, a side panel with three tabs: World (calendar, seasons, the two fields, the star, the four faces, the explorers, the Dice System's other worlds, the Umbrella Tree Zinnia, nations, "Still unwritten"), Regions (every place with its current light phase, with the World file JSON export at the bottom), Place (one card: phase of day, facts, chart, draft lore with an "Edit lore" button saved per browser). The HUD scrubs the day and the year; rain falls on the Canon face in rain season; the star's elevation follows the seasons.

## 3. The canon ledger (Ruby's words, via Joshua)

Quoted lines are verbatim from Joshua's relays (Messenger screenshots transcribed, or his own messages). Unquoted lines are paraphrases carried over from the earlier build notes; treat them as reliable in substance, not in wording. Items marked (v10) were implemented in this round; everything else was already in place before it, and the exact earlier version is not recorded here.

### The world and the calendar
- Tetra: "A single world, a thousand stories". Part of The Dice System ("Worlds beyond chance"; "Different worlds. Same imagination."). Tetra spins leftward; "A slower turn, a richer world." (from the art)
- Calendar: 13 months of 28 days, in order January, February, Tredesember, March, April, May, June, July, August, September, October, November, December, then "the restart day(s)". The build uses one Restart Day (365-day year); a second one is listed under "Still unwritten".
- Seasons "all on average", on the main (Canon) face: rain season = January + the Restart Day; spring = February, Tredesember, March; summer = April, May, June; fall = July, August, September; winter = October, November, December.
- "the inverted planet is a 16x16x16 cube (inside) overworld cave biome" (another Dice System world; listed in the World tab).
- "The umbrella tree zinnia It culd be a element of our world (by the way the stem is not wood and the top is petals)". Where it grows is unwritten.
- Day names, hours in a day and the size of the world are not yet defined (listed as "Still unwritten").

### Fields and the star
- Two fields: a magical field that slows light ("Here, the morning moves slower. And light flows like gold.") and a magnetic field that guides worlds. (from the art)
- "the magnetic field and magical field go all the way around" (v10: both drawn as full rings; the Codex says so).
- "make the sun a dark purple star and the magical field turns its light to the same color of our sun light" (v10: purple star glow in the sky and page gradient; the ground still lights in sun colour, which is her rule; new "The star" entry in the World tab).
- 2026-10-03, Ruby herself in the Claude Code session: "what is that purple light?" Answered: it is the dark purple star she asked for; the ground stays sunlight-coloured because the magical field turns the light, her rule. No change made.
- "The far side does not have high sun, or deep night." (v10: the Far face's lighting is clamped in the shader and on the cards; a year-long sweep shows only First light, The slow morning, Late light, Dusk there.)

### Spikia and Wetia (across faces)
- All the top corner lands (the spikes of the Canon, West and South faces) are one country, Spikia; pronounced sp-īk-iə, also written Spikya.
- "the area on the top of the west side is connected to the top area on the cannon side". "The top connects again" (South).
- All deltas are one nation, Wetia; the three deltas meet at the one corner where West, South and Far touch (V3). "For the third time the delta is called wetia" (v10: all three delta markers are now named Wetia, kind Nation).

### Canon face
- Regions: Whiteland, Yolkia, Islandia, The Headlands (the rooster-head landmass), Neckia, The Feathers, Llamaland, Footia (from the art).
- "Discovered kingdoms in the area (compairing to the map "farword") of the sentral island (Area on the edge and NOT the area on the spike)": the four kingdoms Unoooland (jungle), "It's Hot" (sweltering; "the hot nation"'s name is "It's Hot"), Rainia (rain), Uohia (forest) are on the far side of the Canon face, between Islandia and the far edge. (corrected in an earlier round from a placement on the West island)
- "Why is the cannon face untouchable? It should be touchable" (v10: taken as permission to edit the Canon face, but she gave no Canon change, so her painting is untouched; separately, tapping any face now opens its card on phones). **Ask her which she meant.**
- 2026-10-03, Ruby herself: "why did the cannon face not change?" Answered: the Canon face is her painting and is only changed when she says what to change; she gave no Canon change in round 10. Asked her what she wants changed on it, and which meaning of "untouchable" she meant. No change made.

### West face (Sapphire the explorer)
- Rough map "discovered by sapphire the explorer": the spike at the top, a central island marked with a blue X, a small tropical island Tropicia, a delta (Wetia) at the corner. "forest" on the island.
- The central island's five nations: Swampland, Greenia, Marshia, Greeneria, Baiuland. Spellings confirmed in v10: "Mtlshia → Marshia; Tueldan → Baiuland; Greeneria is correct" (the "spelling?" tags are gone).
- "remove tropical and swamp (west)" (v10: the Tropical strip and The Swamp are gone from the map and the Codex).
- "The islands are connected to each other and the land" was a complaint about v9 (v10: the island, Tropicia and Spikia are separate landmasses again; the "blocky" edge tabs are gone).

### South face (Amethyst the explorer)
- Tropical at the top (Spikia, marked in blue), a continent in the middle sea with the nations Snowia, Coldland, Beria, a delta (Wetia) in the right-hand corner. Snowy tundra at the bottom was removed on request ("remove snowy tundra").
- "Wait the southern continent isn't an island" and "the south continent is supposed to be connected with tree land and the far side but not west" (v10: the continent touches only the bottom edge, shared with the Far face, where it meets Tree Land; it no longer touches the West edge. Verified on the rendered map: the continent's landmass touches the Far edge at t = 0.30 to 0.54 and no other edge).
- "it got the south continent shape wrong": the continent shape is Ruby's outline from Amethyst's sketch (`blobs.py`, `cont_sketch`), fitted inside the face.

### Far face (Obsidian the explorer)
- "far" extreme mountains, a delta (Wetia), nations Warmia and Ehia by the Canon side, Tree Land by the South side. Snowy tundra removed on the same request.
- "extend the extreme mountains to the center of the far side"; Mount Celestial lies at the exact centre; "is it always twilight there???" (v10: the ridge runs from the apex to the centre; `celestial` marker at the exact centre (512, 657.49); its card reads "Twilight, always". **Answer for Ruby: yes.** The centre of the Far face is where the spin axis comes out, so Mount Celestial never turns toward or away from the star; the light only shifts a little with the seasons.)
- "make ehia on land on the far side" (v10: Ehia is on the Canon-side land, south of Warmia).
- "extend tree land to connect with the south continent" (v10: Tree Land's coast crosses the South edge into the continent's lobe).
- 2026-10-03, Ruby herself: "why are treeland and the cannonward nations on the far face not conected?" Her Far nations sketch (`reference/ruby/far_nations.png`) draws Warmia, Ehia and Tree Land inside one outline, one landmass down the Canon side and along the bottom. v10 has Tree Land as a separate landmass at the bottom centre with sea between it and Ehia's land (`design_far` in mapgen2.py builds them as separate masses). That is a build reading, not something she asked for. **Not yet changed: waiting for her to confirm she wants them joined.** Doing it means a land bridge from Ehia into Tree Land inland of the bottom edge (the shared edge 2-3 stays water at t 0.10 to 0.30, so the South face does not change) while the Far face stays at least half water (0.518 now).

### Process rules Joshua gave
- "dont use the exact pictures of the explorers (opal the explorer went back and made comlpete maps of them [generate maps based on the schetches please])"
- "Make shure landmasses line up on all sides so there isn't any land side water things"
- "it still does not meet the (at least half water) ratio" (now asserted in the generator: West 0.61, South 0.503, Far 0.518 water)
- "instead of having one big region it shows you the nations without clicking on the (island/continent) first" (nations are direct markers; the island and continent close-ups are charts on the nation cards)
- "All sides need this level of detail" (with the Canon art attached): the side faces are painted with patches harvested from the Canon art itself.
- "why did it only use my bace as a outline to keep the islands the same but change everything else": use Ruby's drawings as the baseline (thin lines are lines, arrows point to biomes and climates).

## 4. What changed in version 10 (this round)

Maps (`mapgen2.py`, `edges.py`, `texsynth.py`, `paintface.py`, `nations.py`):
- Rounded, noisy edge-conform bands instead of rectangular tabs; sea painted as one normalised layer (no patch grid).
- West: Tropical and The Swamp removed; island nations renamed; island and Tropicia moated so nothing joins.
- South: continent detached from the West edge, joined to the Far edge through a southern lobe; Spikia wedge and the delta shrunk to keep water >= 0.5 (0.503).
- Far: ridge from the apex to the exact centre, Mount Celestial at the centre, Ehia moved onto land, Tree Land at the bottom centre meeting the continent; water 0.518.
- Designed edge `2-3` changed to water (0.10, 0.30) and (0.54, 0.80); `edge_profiles.json` regenerated.

Page (`template.html`, `build.py`):
- Names: Wetia for all three deltas; Marshia, Baiuland; no "spelling?" tags; Mount Celestial card (kind Peak).
- Fields drawn as full rings (3 gold, 3 blue), legend and Codex text "all the way around"; new "The star" section; purple star glow; page gradient purple.
- Far-face light clamp (`uFar` uniform; `phaseFor`), Mount Celestial pinned to "Twilight, always".
- Tapping a face opens the Codex on phones too (`selectFace`: `if(!fly||W>=820)openCodex(true)`).
- "Where the Umbrella Tree Zinnia grows" added to Still unwritten. Nation list note no longer mentions uncertain spellings.
- `window.tetra.phase(id)` added to the debug hook for the tests.

## 5. Open questions for Ruby (do not guess these)

1. "Why is the cannon face untouchable? It should be touchable": did she mean the page (tapping the Canon face on her phone did nothing before v10, fixed) or that the Canon painting may be edited (nothing was changed on it)?
2. One Restart Day or two?
3. Day names, hours in a day, the size of the world.
4. Where the Umbrella Tree Zinnia grows.
5. Lore: every card's prose is first-pass draft marked "Nothing written yet" or draft text for Joshua to edit. None of it is canon.
6. (2026-10-03) Join Tree Land to Ehia and Warmia on the Far face? Her sketch says they are one land; she asked why they are not connected. Waiting for her yes, and whether she wants a wide land or a thin bridge.
7. (2026-10-03) What, if anything, she wants changed on the Canon painting itself.

## 6. Known limits and caveats

- The Far-face clamp also applies to the Extreme Mountains marker and to Wetia's Far-face delta (they are on the Far face). Ruby said "the far side", which was read as the whole face.
- The Far face is the base the world spins on; its centre is on the axis, so in the model its light hardly changes through a day. The clamp makes the cards and the shading agree with Ruby's rule rather than with the geometry alone.
- `texsynth.py` harvests patches from `art_latest.png` with hard-coded art-pixel geometry: the label rectangles (`LABELS`), the painting's outer diamond (`MAP_POLY`), the glow-line corridors and the `rim` segments. If the Canon art changes, all of them must be re-checked or text fragments will leak into the side faces.
- `bake.py` asserts the art is 1448x1086 and hard-codes, in art pixels, the kite points A, P, D, Q, the radial warp centre `ck` (727, 530) and the 13 Canon region positions in `regions`. A new painting needs all of these re-measured; the barycentric assert only catches a region that lands outside the triangle. `bake.py` also writes `tex_west/south/far.jpg`, placeholder stone that nothing reads (gitignored).
- `geometry.json` (from `bake.py`'s `regions`) still names the `hotland` region "The Hot Kingdom". The page shows Ruby's "It's Hot" because `WORLD.places.hotland` overrides the name, but the old string ships inside the GEOMETRY JSON in `dist/`. Fix it in `bake.py` and `geometry.json` at the next content round (it changes `dist/`), then add the name to `RETIRED` in `tools/audit.py`.
- `edge_profiles.json` is a cache: delete it whenever `tex_canon.jpg` or the designed intervals change, or the maps will conform to stale edges.
- The Messenger screenshots from Ruby that drove rounds 6 through 10 are not in this repo (they were pasted into the chat); their content is transcribed in section 3. The sketches that are on disk are in `reference/ruby/`.
- The island outline and the continent outline are hand-typed polygons (`blobs.py`); photo tracing (`legacy/trace.py`) was unreliable and is kept only for reference.
- Lore edits are stored in the viewer's browser only (`localStorage`), not in the file.

## 7. Suggested next steps

- Put Joshua's answers to section 5 into the ledger, then into `WORLD`.
- When Ruby sends the next round: follow "How a round from Ruby is processed" in `CLAUDE.md`.
- Nice to have, not asked for: a visual diff of `map_*.jpg` against the previous version so map rounds show what moved. (`make audit` already covers em dashes, retired names and placeholders.)

## 8. Working with Joshua on this

- He relays Ruby's messages as screenshots; transcribe them before acting and quote them back in the report.
- He wants the work tested before he sees it, and the report in Ruby's terms: for each of her lines, what it became, and which lines needed a reading.
- No em dashes, in anything.
- Pasted AI-written reviews of the work are working input; do not flag them.

## 9. Received into the repository (2026-10-02, Claude Code)

- Where: `OakandSparrowSystemsEnterprises/Cats`, branch `ccr-7fbf7180-0d9gil`, folder `tetra/`. Both companion archives are unpacked into `reference/`, so the repository holds the whole package.
- Verified from the checkout, with Python 3.11, numpy 2.4, OpenCV 4.14, Playwright 1.56 and Chromium 141: `make build` reproduces `dist/` byte for byte from the shipped inputs; `make maps` reproduces all eight JPEGs, `map_anchors.json`, `water_fractions.json` and `edge_profiles.json` byte for byte; `make check` gives the six agreements listed in `CLAUDE.md` (worst 3.7%); `make test`, `make seams` and `make audit` pass. The seam screenshots and the walkthrough screenshots were looked at.
- With OpenCV 5.0 the maps come out pixel-identical within JPEG noise (land/water masks 99.996% to 100% the same, anchors and fractions identical) but not byte-identical. `requirements.txt` therefore pins `opencv-python-headless<5`.
- Changes made on receipt, none of them to the page or the maps:
  - `tests/_page.js` exports `isNetworkError`; `smoke.js` and `walkthrough.js` use it instead of the `ERR_TUNNEL` special case. The page's only external fetch is the Google Fonts stylesheet; when it fails (offline, a proxy, an untrusted certificate) Chromium logs a `net::ERR_*` console error that is not the page's fault. In this environment the first run failed on `ERR_CERT_AUTHORITY_INVALID` for exactly that reason.
  - `requirements.txt`: the OpenCV pin above.
  - `package-lock.json`: the `name` field now reads `tetra` (it was generated in a folder called `scratchpad`).
  - A root `CLAUDE.md` in the repository points at `analyses/` and `tetra/`.
  - `tools/audit.py`: the em-dash scan now covers every text file in the repo (legacy scripts, archived tests, tools, `reference/*.md`, Makefile, manifests); retired-name and placeholder checks are unchanged.
  - `.gitignore`: `pipeline/tex_west.jpg`, `tex_south.jpg`, `tex_far.jpg` (written by `bake.py`, read by nothing). `bake.py`'s docstring now says so.
- Doc corrections, from an audit of `CLAUDE.md`, `HANDOFF.md` and `reference/README.md` against the code (each point was checked by two independent readers before it was changed):
  - The World file JSON export sits at the bottom of the Regions tab, not in the World tab; the World tab also lists the explorers.
  - The page's fonts are Cinzel, Cormorant Garamond and IBM Plex Sans from Google Fonts. Lora is only baked into the Codex chart JPEGs by `mapgen.py`.
  - `bake.py` hard-codes more than the kite points (warp centre, 13 Canon region positions) and writes three unused textures.
  - `mapgen.py`'s main still writes the same output files as `mapgen2.py`; the docs now say never to run it directly.
  - `tests/phases.js` bans six phases on the Far face for a fixed list of five ids, not just High sun and Deep night.
  - The audit's real scope is stated; `make test` and `make seams` rebuild `dist/` first; `check_markers` wants 14 px from the coast; `blobs.json` has no reader; `tools/` is in the layout; `lore` covers the eight painting regions only.
  - `geometry.json` still carries "The Hot Kingdom" for `hotland` (section 6).
  - `reference/README.md` now describes this folder as it is; its unzip instruction pointed at the wrong level (the archives carry a `tetra/` prefix).
- Still not on disk: Ruby's Messenger screenshots from rounds 6 to 10 (section 6).
