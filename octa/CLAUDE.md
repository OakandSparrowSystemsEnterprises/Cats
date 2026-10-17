# Octa, the eight-sided planet (The Dice System)

Octa is the third world of Ruby's Dice System, the d8, added on 2026-10-17 (Ruby: "cool now lets add octa (or octo ...)"). It ships inside Tetra's page, like Hexa: `pipeline/world.html` is a fragment (scoped CSS under `#oapp`, ids starting with `o`, the hook `window.octa`) that `../tetra/pipeline/build.py` inserts at `{{OCTA}}`. It has no map pipeline yet: nothing on it is discovered or drawn (Ruby: "so the first side hasent been discoverd or drawn yet"), so the fragment draws its eight blank sides itself, on a canvas, each with its number on the die. Tetra's rules apply (read `../tetra/CLAUDE.md`): never invent canon, no em dashes anywhere, test before shipping, Ruby's spellings exactly inside quotes. Read `HANDOFF.md` for the ledger and the open questions.

## What exists (draft 1, 2026-10-17)

- The name: Octa, by the vote Ruby called for ("me, daddy, and you will vote (daddy votes octa, i vote octo)"): Ruby Octo, Daddy Octa, Claude Octa (the hedron rule she set when renaming Cuba, and the family sound of Tetra, Hexa, Octa, Deca, Dodeca). Two to one. She can overrule it.
- The sides: eight, named by their number on the die for now (Ruby: "the sides are just named by the number on the dice"), until she picks two more directions to join Hexa's six or keeps the numbers. The World tab lists five candidate pairs she asked for ("give me at least 3 examples"): Dawn and Dusk, Zenith and Nadir, Windward and Leeward, Over and Under, Sunward and Starward, plus the corner-naming idea as a reading. None is chosen.
- The die: a regular octahedron (`R` = 1.45, corners on the axes). `OCTANTS` gives each number its octant: 1, 3, 5, 7 round the top corner (1 facing the viewer at the start, then round to the viewer's left), 2, 4, 6, 8 their opposites, so opposite sides add up to 9 as on a d8. Which number sits where is a reading. Each side's picture (`sidePicture`) is slate with a dashed edge, its number and "not yet discovered"; `TEX_SCALE` maps the side's own plane onto a 512 px canvas.
- Nothing else is written, so nothing else is drawn: no star of its own (the faces are lit from the viewer's side), no moon, no fields, no turn (the viewer orbits a still die), no calendar. The dock shows the Dice System's shared clock as a day count ("Shared clock · day N"), the Spin slider and Play/Pause act on that shared clock (`dice.time`, through getters on `state` as in Hexa), and the eight side buttons fly the camera to each side.
- Codex: World (the world, the vote, the directions question, the Dice System list, Still unwritten), Sides (the eight, each "Not discovered or drawn yet", side 1 in Ruby's words), Side (the chosen side's card with its opposite).
- Hook `window.octa`: `state`, `facing()`, `sides()`, `opposite(id)`, `face(id, fly)`, `setYaw(yaw, pitch)`, `setSpin(on)`, `syncTime()`, `centre(id)` (screen point of a side's centre), `sample(id)` and `sampleAt(fx, fy)` (pixels). `../tetra/tests/octa.js` uses them.
- Bridge: `dice.ready('octa', start)` and `dice.snapshot('octa', ...)` (baseYaw, pitch, dist, selectedSide); `dice.show('octa')` toggles `away` on `#oapp`; `dice.world` reads `octa` when it is shown.

## Build, test, ship

From `../tetra/`: `make build` (inserts this fragment), `make test` (includes `tests/octa.js`), `make audit`. Ship both files from there, as for Tetra and Hexa.
