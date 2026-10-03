# Handoff: Tetra, version 11 (2026-10-03)

Written for the next Claude Code session picking this up from the Claude app conversation where versions 1 through 10 were built. Read `CLAUDE.md` first for the rules and the layout; this file is the state.

## 1. What is shipped

- **Version 11 (2026-10-03)** is the current build in `dist/`, made in the repository from Ruby's round of 2026-10-03 (sections 3 and 10): the Canon face generated like the other faces, Tree Land joined to Ehia, the d3 moon, the count of years, her key events. Screenshots in `reference/screenshots-v11/`. See section 10 for the publishing status.
- Version 10 (2026-10-02), the previous build, is what the lines below describe:
- Published artifact: `https://claude.ai/artifact/G6JjTxacMzAGCtcSrETb8v`. Version 10, label "v10 Ruby's fixes, purple star, rings", was published 2026-10-01 from `dist/tetra.html`; version 11 replaced it on 2026-10-03 (see section 10).
- Standalone copy sent to Joshua the same day: `dist/tetra_world.html` (identical content, wrapped in a full HTML document).
- Both files in `dist/` are byte-identical to what was published (verified by rebuilding from a clean copy of this repo on 2026-10-02: `make maps && make build` reproduces them, `make test` passes). Re-verified from the repository checkout the same day, see section 9.
- Screenshots of v10 are in `reference/screenshots-v10/` (desktop home, each face, the Mount Celestial card, the World tab, phone views, the six-seam sheet).

## 2. What the page does

A tetrahedron (four equilateral faces) spins leftward once per world day under a dark purple star. All four faces carry generated maps in the same painted style; the Canon face's outline and its 13 places come from Ruby's painting (since v11; before that the face showed the painting itself). HTML markers sit on the faces; tapping a marker or a face opens the Codex, a side panel with three tabs: World (calendar with the count of years, seasons, the two fields, the star, the moon, the four faces, the Dice System's other worlds, the Umbrella Tree Zinnia, nations, the explorers, the key events, "Still unwritten"), Regions (every place with its current light phase, with the World file JSON export at the bottom), Place (one card: phase of day, facts, chart, draft lore with an "Edit lore" button saved per browser). The HUD scrubs the day and the year; rain falls on the Canon face in rain season; the star's elevation follows the seasons.

## 3. The canon ledger (Ruby's words, via Joshua)

Quoted lines are verbatim from Joshua's relays (Messenger screenshots transcribed, or his own messages). Unquoted lines are paraphrases carried over from the earlier build notes; treat them as reliable in substance, not in wording. Items marked (v10) were implemented in this round; everything else was already in place before it, and the exact earlier version is not recorded here.

### The world and the calendar
- Tetra: "A single world, a thousand stories". Part of The Dice System ("Worlds beyond chance"; "Different worlds. Same imagination."). Tetra spins leftward; "A slower turn, a richer world." (from the art)
- Calendar: 13 months of 28 days, in order January, February, Tredesember, March, April, May, June, July, August, September, October, November, December, then "the restart day(s)". The build uses one Restart Day (365-day year); a second one is listed under "Still unwritten".
- Seasons "all on average", on the main (Canon) face: rain season = January + the Restart Day; spring = February, Tredesember, March; summer = April, May, June; fall = July, August, September; winter = October, November, December.
- "the inverted planet is a 16x16x16 cube (inside) overworld cave biome" (another Dice System world; listed in the World tab).
- "The umbrella tree zinnia It culd be a element of our world (by the way the stem is not wood and the top is petals)". Where it grows is unwritten.
- Day names, hours in a day and the size of the world are not yet defined (listed as "Still unwritten").
- 2026-10-03, Ruby: "reset dayes are one and a quarter days so there arent leap years" (v11: the Restart Day is 1.25 days long, so the year is 365.25 days and there are no leap years: `WORLD.calendar.yearDays` 365.25, `restartDays` 1.25; the HUD shows "Restart Day · 1¼ days" and "of 365¼"; the day slider still runs 1 to 365, the last position being the whole Restart Day. Reading: "reset day" = the Restart Day, one of them (answers open question 2: no second Restart Day).)

### Fields and the star
- Two fields: a magical field that slows light ("Here, the morning moves slower. And light flows like gold.") and a magnetic field that guides worlds. (from the art)
- "the magnetic field and magical field go all the way around" (v10: both drawn as full rings; the Codex says so).
- "make the sun a dark purple star and the magical field turns its light to the same color of our sun light" (v10: purple star glow in the sky and page gradient; the ground still lights in sun colour, which is her rule; new "The star" entry in the World tab).
- 2026-10-03, Ruby herself in the Claude Code session: "what is that purple light?" Answered: it is the dark purple star she asked for; the ground stays sunlight-coloured because the magical field turns the light, her rule. No change made.
- 2026-10-03, Ruby: "1: thank you just comfirming." (confirmed, no change)
- "The far side does not have high sun, or deep night." (v10: the Far face's lighting is clamped in the shader and on the cards; a year-long sweep shows only First light, The slow morning, Late light, Dusk there.)

### Spikia and Wetia (across faces)
- All the top corner lands (the spikes of the Canon, West and South faces) are one country, Spikia; pronounced sp-īk-iə, also written Spikya.
- "the area on the top of the west side is connected to the top area on the cannon side". "The top connects again" (South).
- All deltas are one nation, Wetia; the three deltas meet at the one corner where West, South and Far touch (V3). "For the third time the delta is called wetia" (v10: all three delta markers are now named Wetia, kind Nation).

### Canon face
- Regions: Whiteland, Yolkia, Islandia, The Headlands (the rooster-head landmass), Neckia, The Feathers, Llamaland, Footia (from the art).
- "Discovered kingdoms in the area (compairing to the map "farword") of the sentral island (Area on the edge and NOT the area on the spike)": the four kingdoms Unoooland (jungle), "It's Hot" (sweltering; "the hot nation"'s name is "It's Hot"), Rainia (rain), Uohia (forest) are on the far side of the Canon face, between Islandia and the far edge. (corrected in an earlier round from a placement on the West island)
- 2026-10-03, Ruby: "its ughia not uohia" (the forest nation is **Ughia**: renamed in the page, the nations list, the Canon chart label, geometry.json and bake.py; the id stays `uohia`; "Uohia" is a retired name in the audit.)
- "Why is the cannon face untouchable? It should be touchable" (v10: taken as permission to edit the Canon face, but she gave no Canon change, so her painting is untouched; separately, tapping any face now opens its card on phones). **Ask her which she meant.**
- 2026-10-03, Ruby herself: "why did the cannon face not change?" Answered: the Canon face is her painting and is only changed when she says what to change; she gave no Canon change in round 10. Asked her what she wants changed on it, and which meaning of "untouchable" she meant. No change made.
- 2026-10-03, Ruby: "2: the cannon face shuld not have land on the west and east sides and needs to not have clouds, be at least 50% water, and look like the other sides (the detail is too much for the cannon side, this is a 4th of a entire planet you know)" (v11, first design, replaced the same day after her next message, below: the Canon face generated like the other three, from the outline of her painting (`design_canon` in mapgen2.py): open sea along both side edges below Spikia, no clouds, 51.6% water, painted in the same patch style. Readings taken: "west and east sides" = the two side edges of the Canon triangle; Spikia at the top corner stays because she made it one country across the three faces; the bottom edge keeps the painting's coast so the Far face still matches. The open-sea band along the two side edges (`SIDE_SEA`, 96 px, about 9% of the face width) removed the land under her painted Whiteland, the Headlands and Llamaland, which moved 40, 44 and 38 px inland to the new coast; the coast was then pulled in to reach half water (9 px, scaled by local land thickness so the egg of Whiteland and Yolkia and the rooster of the Headlands keep their width), which moved Footia 17 px and It's Hot 7 px. The Canon regions' names and order are still the painting's. Two more readings: the two bottom corners of the face stay land, because the bottom edge is her painted coast and is land at both ends, and the Far, West and South faces are land at those corners too, so the far-side land touches the last 7% of each side edge (`CORNER_T` in edges.py; open question 12); and the painting's rivers, including the one between Whiteland and Yolkia, are not reproduced, the generated face has its own rivers from Spikia and the Feathers.)

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
- 2026-10-03, Ruby, on seeing that first generated Canon face: "what hapend to the cannon face!?!? we need to make islandia, egg island, and chicken island smaller so they can keep their shapes and for the south continent, make it sort of semi circly please" (v11, the design that shipped: the painting's three islands are cut out whole (`canon_pieces`: the egg = Whiteland and Yolkia; the chicken = the Headlands, Neckia, the Feathers, Llamaland and Footia; Islandia) and scaled down about their own centres so they keep their shapes (`place`; egg 0.48, chicken 0.53, Islandia 0.43 of the painting's size, the largest sizes that leave 40 px of water between them once the egg and the chicken sit clear of the side sea), and the southern land is a half-disc standing on the middle of the bottom edge (`dome`, 580 px wide, 213 px tall, as tall as a 40 px channel to the islands allows); the face is 59.8% water. Readings: "south continent" = the Canon face's bottom land, the one with the four nations (the Southern Continent on the South face is unchanged; open question 13 asks); the half-disc is centred on the bottom edge and the four nations keep their painted places (Ughia 7 px inland); the painting's small islets are dropped.)
- 2026-10-03, Ruby, on the second design: "make it as tall as that but have the semi sircle be more like a 6th of a circle and make egia and islandia perfectly shperical plz also put the chicken island above islandia now that we have the room" (v11, the design that shipped, `design_canon` third version: egg island ("egia") and Islandia are perfect discs (`disc`, radius 66 and 50 px, sizes are a reading; Whiteland on the egg's west half, Yolkia on its east half, 16 px inland); the egg sits where the painting's egg was, slid clear of the side sea, and Islandia keeps 40 px of water from it, which puts Islandia a little right of the middle; chicken island keeps its painted shape and sits above them (`place`), its width centred on the face, as big as fits between Spikia's coast and Islandia with 40 px channels (0.40 of the painting's size); the southern land keeps the half-disc's height, 213 px (`DOME_H`), and is a flatter arc (`arch`): the sixth of a circle she asked for would be a circle of radius 1590 px, and the face stays half water only up to radius 1251, so the arc is as flat as the water rule allows, about a seventh of a circle as far as it shows within the face; water 0.507. Reading: "6th of a circle" = a flatter curve of the same height, not a pie slice.)
- 2026-10-03, Ruby, on the third design: "whiteland and yolkia need to have a rivver on the border and egg island shuld be egg shaped (also no perfict circular stuff. farthern contenent is good." (v11: egg island is an egg (`egg_shape`, 58 x 76 px, narrow end up, tilted, with a slightly wandering coast), Islandia is round but not perfectly (a wobbled disc), and a river runs down the egg's long axis, the border between Whiteland (west) and Yolkia (east): a shallow valley along the axis, highest at the north end, with the river rising there and flowing south to the sea. The southern arch is unchanged ("farthern contenent is good" read as the southern land).)
- 2026-10-03, Ruby: "not Unoooland, Uncooland" (the jungle nation is **Uncooland**: renamed in the page, the nations list, the Canon chart label, the key events, geometry.json and bake.py; the id stays `unoooland`; "Unoooland" is a retired name in the audit.)
- 2026-10-03, Ruby, asked whether Tree Land should join Ehia and Warmia: "3: yes pleese" (v11: a neck of land runs from Ehia down to Tree Land, inland of the South edge, so the South face is unchanged there. She did not say wide or thin; it is about 90 px wide, as her sketch's single outline suggests. To keep the Far face at half water (0.504) the Extreme Mountains ridge is a little slimmer (rx 66 to 60) and Wetia's delta lobe a little smaller (108x82 to 102x78); nothing else moved.)
- 2026-10-03, Ruby herself: "why are treeland and the cannonward nations on the far face not conected?" Her Far nations sketch (`reference/ruby/far_nations.png`) draws Warmia, Ehia and Tree Land inside one outline, one landmass down the Canon side and along the bottom. v10 has Tree Land as a separate landmass at the bottom centre with sea between it and Ehia's land (`design_far` in mapgen2.py builds them as separate masses). That is a build reading, not something she asked for. Done in v11 after her "yes pleese", see the line above.

### The moon
- 2026-10-03, Ruby: "4: we bouth agree that the moon of tetra is a d3 (with one crater on the one side, two craters on the two side, and three craters on the three side)(perferably NOT the cubic d3(its dumb))" (v11: "The moon" entry in the World tab and `WORLD.moon` in the world JSON. At first not drawn in the sky, see the next line.)
- 2026-10-03, Ruby: "for the moon, it shuld be a 1/3 of the size of tetra and solar eclipse every month on the new moon, but every other day it is just on oposite side of sun, and is a little bit farther than the magical field." (v11: the moon is a real body now (`moonState`, `moonScreen`, `drawMoon`): a three-sided die a third of Tetra's edge long (`MOON_LEN`), orbiting at 2.48 world units, just outside the outermost gold ring at 2.18 (`MOON_ORBIT`); on every ordinary day it sits exactly opposite the star; on the new moon it swings once round its orbit over the day, through the line to the star at midday, and the world darkens (the star's light and the ambient light dim, the star's glow fades) while it covers the star (`MOON.eclipse`). Readings: "the size of Tetra" = the length of an edge; "a little bit farther than the magical field" = 0.3 beyond the last gold ring; the new moon falls on the first day of each month (she has not said which day, open question 15); the swing takes the whole new-moon day; drawn behind the world on the stars layer and in front of it on the overlay, so the world hides it or it hides the world as it should.)
- 2026-10-03, Ruby: "also where is the moon???" (v11: the d3 is drawn in the sky (`drawMoon` in template.html): a three-sided rolling die seen from the side, its one-crater and two-crater faces showing and the three-crater face turned away, lit from the star. Its size, distance and path are not written, so it hangs at a stand-in spot (`MOON_SPOT`, 3.9 rad round from the star, chosen so it is in view on the home screen on desktop and phone) at a stand-in size (`MOON_SIZE`); the Codex says so, and Still unwritten still lists the moon.)

### Years and the key events
- 2026-10-03, Ruby: "5: dad will send you some comics i made on kea events, the number is the year, negaive years is the same as bce on earth (also -0 and 0 are not the same year) (im not done with it yet but i got to around year 1 and it is curently around year 1750 of earth in teck and in tetra years they are in 1700" (v11: calendar rows "Years" and "Now" in the World tab; the HUD counts years from 1700 (`YEAR0`); a "Key events" list in the World tab from the two comic pages she then sent herself; "the key events after year 0" under Still unwritten.)
- 2026-10-03, Ruby, with the two pages: "sorry about the blurryness in the first comick hopefully you can read it". The pages are `reference/ruby/comics/key_events_p1.jpg` and `key_events_p2.jpg`. Panel by panel, as read from the photos ((?) = hard to read, to be confirmed by her):
  - -2000: "octal una terra" (?) over green hills and a figure.
  - -1000: "Dote" (?), a figure on a green hill.
  - -500: a die with dots and a figure saying "runder tot raen?" (?).
  - -100: "ohiy" (?) and "boing" (?), and a word written across the green land; a small figure standing in the water, and something orange afloat.
    - 2026-10-03, Ruby, on the hard-to-read words: "-2000: \"estar una tetragon\"? -1000 corect -500 \"runder tetragon?\" -100 (two different combinations of adios and bye) -1 its ughia not uohia and the fourth name is not importnt right now." (the Key events list now reads estar una tetragon, Dote, runder tetragon?; the two -100 bubbles are described as goodbyes mixing adios and bye, their letters still marked (?); the forest nation is Ughia everywhere, see the Canon face lines; the fourth -1 name stays unread by her choice.)
    - 2026-10-03, Ruby, on this panel: "someone was venturing out to explore from what was to be named uncooland to find other landmasses" (the panel's caption in the Key events list is now her explanation. She wrote "uncooland" here and "Unoooland" in every earlier round, so the page keeps Unoooland until she says which; open question 8.)
  - -90: a great hand, no words.
  - -50: "d3?!": a figure on the ground looks up at a d3 (the moon, by her point 4).
  - -10: "we split up!!": Whiteland and Yolkia drawn as the egg-shaped land in the sea.
  - -5: "we unco..." (the rest runs off the page), a green hill.
  - -1: "its hot!", "Ughia" (read as Uohia at first), "rainyia?" and one more name (?): four name bubbles over a green hill with question marks all around (three of them are her far-side Canon nations).
  - -0: "0-0?!" and a bird on the face.
  - 0: "posibly central island located", "yay!", "ISLANDIA!": people cheering, the name Islandia in big letters.

### Process rules Joshua gave
- "dont use the exact pictures of the explorers (opal the explorer went back and made comlpete maps of them [generate maps based on the schetches please])"
- "Make shure landmasses line up on all sides so there isn't any land side water things"
- "it still does not meet the (at least half water) ratio" (asserted in the generator for every face; the measured fractions are in `pipeline/water_fractions.json` and in the current version's section: v11 Canon 0.516, West 0.69, South 0.561, Far 0.504)
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

1. (Answered 2026-10-03: she wanted the Canon face itself changed, see her point 2 in section 3; done in v11.)
2. (Answered 2026-10-03: one Restart Day, one and a quarter days long, so there are no leap years.)
3. Day names, hours in a day, the size of the world.
4. Where the Umbrella Tree Zinnia grows.
5. Lore: every card's prose is first-pass draft marked "Nothing written yet" or draft text for Joshua to edit. None of it is canon.
6. (Answered 2026-10-03: "yes pleese"; done in v11, about 90 px wide. She can still say wider or thinner.)
7. (Answered 2026-10-03 by her point 2; done in v11.)
8. (Answered 2026-10-03, see section 3: estar una tetragon; Dote; runder tetragon?; the -100 bubbles are goodbyes mixing adios and bye; Ughia not Uohia; Uncooland not Unoooland; the fourth -1 name is not important right now.)
9. (2026-10-03) "We split up!!" at year -10 shows Whiteland and Yolkia parting. On the generated map they are still one land, with no river between them (the painting had a river as their border, and the draft lore still says so). Should they be two separate lands now?
10. (Answered 2026-10-03: a third of Tetra's size, just outside the magical field, opposite the star on ordinary days, an eclipse every month on the new moon. Still open: which side of the die faces Tetra.)
11. (2026-10-03) Does she want the comic pages themselves shown in the Codex, or only the list of events?
13. (Answered 2026-10-03 in effect: her next message called the Canon face's bottom land "the semi sircle" and shaped it further, so the reading was right. The Southern Continent on the South face is unchanged.)
15. (2026-10-03) Which day of the month is the new moon? The eclipse is drawn on the first day of each month for now.
14. (2026-10-03) Chicken island came out small (0.40 of the painting) because it has to fit between Spikia's coast and Islandia with water around it. If she wants it bigger, Islandia or the egg could sit lower, or the southern arch a little lower.
12. (2026-10-03) The two bottom corners of the Canon face are land: the far-side land reaches them, because the bottom edge is her painted coast and the three other faces are land at those corners. Her words were "no land on the west and east sides". May the corners stay land, or should they be water too? Water there would also change the Far face's Canon-side coast.

## 6. Known limits and caveats

- The Far-face clamp also applies to the Extreme Mountains marker and to Wetia's Far-face delta (they are on the Far face). Ruby said "the far side", which was read as the whole face.
- The Far face is the base the world spins on; its centre is on the axis, so in the model its light hardly changes through a day. The clamp makes the cards and the shading agree with Ruby's rule rather than with the geometry alone.
- `texsynth.py` harvests patches from `art_latest.png` with hard-coded art-pixel geometry: the label rectangles (`LABELS`), the painting's outer diamond (`MAP_POLY`), the glow-line corridors and the `rim` segments. If the Canon art changes, all of them must be re-checked or text fragments will leak into the side faces.
- `bake.py` asserts the art is 1448x1086 and hard-codes, in art pixels, the kite points A, P, D, Q, the radial warp centre `ck` (727, 530) and the 13 Canon region positions in `regions`. A new painting needs all of these re-measured; the barycentric assert only catches a region that lands outside the triangle. `bake.py` also writes `tex_west/south/far.jpg`, placeholder stone that nothing reads (gitignored).
- (Fixed in v11: `geometry.json` and `bake.py` now name the `hotland` region "It's Hot", and "The Hot Kingdom" is in `RETIRED`.)
- Chicken island is read off the painting by colour (`canon_outline`: sea by the blue classifier, clouds by brightness and low saturation, filled from their surroundings) and cut from the landmasses it touches by nearest region marker (`canon_pieces`), then scaled and moved (`place`); a different painting, or a different classifier threshold, gives a different chicken. Egg island, Islandia and the southern arch are plain shapes (`disc`, `arch`), not the painting's coasts. The 13 Canon positions come from `geometry.json` (measured on the painting) for the chicken and the four southern nations, and are placed by hand for the discs; all are settled onto land by `settle`; `map_anchors.json['canon']` holds where they ended up.
- `edge_profiles.json` is a cache: delete it whenever `tex_canon.jpg` or the designed intervals change, or the maps will conform to stale edges.
- The Messenger screenshots from Ruby that drove rounds 6 through 10 are not in this repo (they were pasted into the chat); their content is transcribed in section 3. The sketches that are on disk are in `reference/ruby/`.
- The island outline and the continent outline are hand-typed polygons (`blobs.py`); photo tracing (`legacy/trace.py`) was unreliable and is kept only for reference.
- Lore edits are stored in the viewer's browser only (`localStorage`), not in the file.
- On a phone, in the starting view, the moon sits just off the right edge of the screen on ordinary days (it is opposite the star, far behind the world, and a portrait screen is narrow); it comes into view when the world is turned a little, and on the new moon it swings across the screen. Turning the default view by a few degrees does not help, because the moon is far behind the world and barely moves on screen; only a much wider view would.

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

## 10. What changed in version 11 (2026-10-03, Claude Code, from Ruby's round of the same day)

Maps (`mapgen2.py`, `edges.py`, `check_edges.py`, `build.py`):
- The Canon face is generated (`design_canon`, three versions in one day, the third shipped): egg island an egg (`egg_shape`, 58 x 76 px, tilted, with the Whiteland and Yolkia border river down its long axis), Islandia a round island with a wandering coast (`disc` with `wobble`, radius 50), chicken island cut out of the painting (`canon_outline`, `canon_pieces`), scaled to fit above Islandia (`place`, 0.40), the southern land a flat arch 213 px tall (`arch`, radius 1251), Spikia's wedge, open sea along the two side edges below Spikia (`SIDE_SEA`), 40 px channels (`CHANNEL`), markers moved with their islands and settled on land (`settle`), painted with the same patches as the other faces, labelled Codex chart `codex_canon.jpg`. Water: Canon 0.507, West 0.69, South 0.561, Far 0.504.
- Edges: `0-1` and `0-2` (the Canon side edges) are designed now: land to t 0.25 (Spikia), water to t 0.93, land in the last 7% (the bottom corners, see the reading in section 3 and open question 12); `1-2` is still measured from `tex_canon.jpg`. The West and South faces re-conformed to the open sea on their Canon sides. Edge agreement: 0-1 99.7%, 0-2 99.3%, 0-3 97.0%, 1-2 100%, 1-3 96.7%, 2-3 97.7%.
- Far: a neck of land from Ehia to Tree Land; the Extreme Mountains ridge and Wetia's delta slightly slimmer to pay for it.
- `build.py` takes the Canon regions from `map_anchors.json` (names and order from `geometry.json`), inlines `map_canon.jpg` as the Canon texture and `codex_canon.jpg` as `{{MAP_CANON}}`. `check_edges.py` measures the Canon side from `map_canon.jpg`.
- `hotland` is named "It's Hot", `uohia` "Ughia" and `unoooland` "Uncooland" in `geometry.json`, `bake.py` and the page; "The Hot Kingdom", "Uohia" and "Unoooland" are retired names in the audit.

Page (`template.html`):
- World tab: "The moon" (a d3, craters 1, 2, 3, not the cube kind), calendar rows "Years" (year 0 and year -0 are different years; negative years like BCE) and "Now" (year 1700, Earth's 1750 in technology), a "Key events" list from Ruby's comics (`WORLD.timeline`), two new Still unwritten items (the moon's size, distance and orbit; the key events after year 0).
- The HUD counts years from 1700 (`YEAR0 = WORLD.years.now`).
- The Canon face card describes the generated face and shows its chart; its note quotes Ruby's instruction.
- The d3 moon as a body in orbit (`moonState`, `moonScreen`, `drawMoon`, `MOON_LEN`, `MOON_ORBIT`, `MOON_TILT`): opposite the star on ordinary days, a full swing with a solar eclipse on the first day of each month; the eclipse dims the star's light, the ambient light and the star's glow. `window.tetra.moon()` returns its screen position, swing angle and eclipse amount for the tests.
- The year is 365.25 days: the Restart Day lasts one and a quarter days (`WORLD.calendar.restartDays`), so there are no leap years; `dateParts` works in fractional days.
- `WORLD.moon`, `WORLD.years` and `WORLD.timeline` are in the world JSON export.

Reference: Ruby's two comic pages in `reference/ruby/comics/`; version 11 screenshots in `reference/screenshots-v11/` (including `moon_*` and `eclipse_*`).

Publishing: `dist/tetra.html` was published to `https://claude.ai/artifact/G6JjTxacMzAGCtcSrETb8v` on 2026-10-03 from the Claude Code session, as version 11 with the label "v11 Canon as a map, Tree Land joined, d3 moon, years", and again the same day with the -100 caption from Ruby's own explanation, and once more with the redesigned Canon face (islands kept, half-disc south) and the d3 moon in the sky (the session had the Artifact tool, so the republish did not need a separate Claude conversation). `dist/tetra_world.html` is the matching standalone file. The artifact is private: Ruby sees it only through the access Joshua has already given, or through the standalone file.
