# Handoff: Cuba, the cube planet (started 2026-10-04)

Cuba is the second world of The Dice System, after Tetra (see `../tetra/`, read its `CLAUDE.md` for the ground rules, which hold here too: canon comes from Ruby by chat, relayed by Joshua; never invent canon; no em dashes anywhere; test before shipping). Nothing is built yet. This file holds her words as they arrive, the readings taken, and the open questions, in the same shape as `../tetra/HANDOFF.md`.

## 1. State

- **Draft 1 (2026-10-04)**: a WebGL cube with six named sides in Ruby's arrangement; the Canon side drawn with her central island, its arms crossing onto the East, West, North and South sides, and the small hole to the Far side; the Far side with the hole's other end; the other four sides uncharted beyond the arm; a Codex with her words and the readings. Built in `pipeline/`, shipped as `dist/cuba.html` (published, see section 5) and `dist/cuba_world.html`. Screenshots in `tests/out/` after `make test`.
- The island is drawn from a written description of her photo (section 2) and her words, not from the photo: the photo itself has not reached the repository. Checking the shape against it is the first thing to do when it arrives (`reference/ruby/README.md`).

## 2. The canon ledger (Ruby's words, via Joshua)

### The world and its sides

- 2026-10-04, Ruby: "so now we need to focus on creating cuba (the cube planet). lets start with a cannon side, a central island whith a small hole (that takes you to the oposite side (the far side)) lies on the cannon side (we are using the same sides as tetra but with east and noth included to make their names for all six sides)(the north is on the top and south is on the bottom) the picture will be coming after this mesage." (Map as read, nothing built: the world is a cube with six sides named Canon, West, South, Far, East and North. North is the top face and South the bottom, so Canon, West, Far and East are the four upright sides, with Far opposite Canon. On the Canon side lies a central island with a small hole that takes you through the world to the Far side. The Canon side comes first; her picture of it is coming.)

### The picture of the Canon side (received as a description)

- 2026-10-04, received in chat as a description of Ruby's photo, not the photo itself; the text reads as AI-written (flagged to Joshua at once; kept here because it is the only record of the picture so far): "The photo is sideways. Imagine rotating it 90 degrees counterclockwise so the notebook's spiral binding runs along the top. The cube net has four squares in a horizontal row, reading left to right: East, Canon, West, Far. North attaches directly above Canon, and South attaches directly below Canon. When folded, Canon is opposite Far, East is opposite West, and North is opposite South. Preserve Ruby's orientation: when looking straight at Canon, North is above it, South is below it, East is to its left, and West is to its right. Below the net is an enlarged drawing of the Canon face. Its outer boundary is square. The internal linework forms a broad, roughly cross-shaped central area, with extensions pointing toward the midpoint of each edge. The four corner areas have recessed boundaries with short rounded or stepped bends where they meet the central area. Use this shape as the reference for Ruby's central island. Some strokes reach the square's edges, but the drawing has no shading or legend establishing whether these represent shoreline, connecting paths, or unfinished boundaries. At the center is a circled handwritten annotation reading 'to far side.' This marks the small hole Ruby described, which takes you through Cuba to the opposite face, Far. The annotation occupies considerable space so it can be read; it does not establish that the actual hole is large. The words are explanatory labels, not lettering to place on the terrain. A curved arrow connects the enlarged terrain drawing to Canon in the cube net. It identifies which face the terrain belongs to. The faint drawings on the right show the cube from different perspectives, including North and South; they do not clearly specify additional terrain." Readings taken for draft 1: the island is a broad cross with an arm toward the middle of each side and rounded bends at the corners, its arms stopping short of the sides (an island, not a bridge; open question 2); the hole is small (2.2% of the face across) and in the middle; the Far side gets the hole's other end, implied by "to far side", and nothing else; the four other sides are plain and marked not yet charted; East is on the left and West on the right of Canon when North is up, exactly as described (it is the mirror of an Earth map, and it is hers); colours are placeholders (nothing said).

- 2026-10-04, Ruby: "wait the squares conect to the north south east and west faces" and, at once, "sorry arms not squares" (answering open question 2 before it was asked: the island's arms reach the four sides of the Canon face and the land connects onto the East, West, North and South sides. Draft 1 was redrawn before shipping: the arms run to the edges, and on each of those four sides a tongue of land continues a short way in (`TONGUE`, 14% of the side) and stops, the rest of those sides staying uncharted slate. How far the land really goes there is open question 2 now. The coast is drawn calm within 48 px of an edge so both sides of each edge agree; `mapgen.py` asserts the agreement.)

### How Cuba was reached, and where it sits

- 2026-10-04, Ruby: "lets imagine that amber the explorer makes a chamber out of a tree and (calculated corectly)launches of ither spikia or the far side using majic, gets flung by the moving moon (going in or out of solar eclipse) gets flung by the star and lands on the cannon face of cuba (year 1650) (also if there were 5 magical fields, and tetra was in the first one, cuba would be in the last one (going away from the star would be the direction they were stacked in))" (recorded as her imagining, her words on the World tab under "How Cuba was reached" and in the "Place" row. Readings: Amber is a new explorer (Tetra's are Sapphire, Amethyst, Obsidian and Opal); the launch place, Spikia or Tetra's Far side, is undecided, open question 6; year 1650 is in Tetra's count (Tetra is at 1700 now); "if there were 5 magical fields" is a picture of where Cuba sits, farther from the star than Tetra, not a statement that there are five, open question 5. Not built: nothing of the flight is drawn.)

## 3. Open questions for Ruby (do not guess these)

1. (Joshua) The photo itself: please put it in `reference/ruby/canon_side.jpg` or send it in chat, so the island can be checked against it.
2. (Answered 2026-10-04: "the arms connect to the north south east and west faces".) Still open: how far the land goes on each of those four sides. Drawn a short way in.
3. Names for the island and for the hole.
4. What is on the Far side around the other end of the hole, and on the other four sides.
5. How many magical fields there are, and whether Cuba shares Tetra's dark purple star and its moon (read as the same star, farther out, from "going away from the star").
6. Where Amber launched from: Spikia or Tetra's Far side.
7. How big Cuba is, which way it turns, how long its day and year are. The spin in the page is a placeholder.

## 4. Where it lives

`cuba/` beside `tetra/`: its own page and pipeline (see `CLAUDE.md` here), built the way Tetra was; it uses Tetra's Playwright install and Python libraries and copies no code. Tetra's Dice System list should name Cuba now that it exists (not done yet).

## 5. Publishing

- Draft 1, 2026-10-04: `dist/cuba.html` published from the Claude Code session as a new artifact (URL below), label "Cuba draft 1: the Canon side"; `dist/cuba_world.html` sent to Joshua. Version 1 drew the cube inside out (clockwise triangles, so the near faces were culled and the inside of the Far side showed where Canon should be); the smoke test had not looked at pixels and passed. Version 2, the same day, fixed the winding and the test now reads the drawn pixels at the island, the hole and the hole's other end.
- Artifact: `https://claude.ai/artifact/JR26dyQ1CbKAHadDZZSSYv` (private; version 1 drew the box inside out and was replaced the same day, see section 1).
