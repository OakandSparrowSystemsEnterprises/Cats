# Handoff: Octa, the eight-sided planet

## 1. State

- **Draft 2 (2026-10-17, later)**: Octa turns under Tetra's star, has a d7 moon (a five-sided prism, fair and no barrel, a reading like Hexa's d5), a year of 15 months of 28 days plus a Restart Day of a day and three quarters (421¾ days; the fifteenth month unnamed, placed after Amberary as a reading), phases on its side cards; five more direction pairs; the planets named by her hedron rule (Icosa, Icositetra). See the second round in section 2.
- **Draft 1 (2026-10-17)**: Octa joins the page as the third world: eight blank numbered sides, the vote on its name, the question of two more directions with five candidate pairs, the shared clock. Nothing on it is discovered or drawn. See section 2.

## 2. The canon ledger (Ruby's words, via Joshua's account)

- 2026-10-17, Ruby: "cool now lets add octa (or octo (whichever sounds better (dont just use the first or secont, me, daddy, and you will vote (daddy votes octa, i vote octo))) the sides are just named by the number on the dice (unless you can preduce 2 more directions on top of Hexa's that fit in(give me at least 3 examples before we resort to the numberd situation)) so the first side hasent been discoverd or drawn yet"
  - The name: a vote, as she asked. Ruby, Octo. Daddy, Octa. Claude, Octa: by the pattern of her Cuba renaming of 2026-10-10 (the planet takes the first half of its hedron's name: tetrahedron, hexahedron, octahedron; a reading at the time, made her rule for every planet later the same day), and because Tetra, Hexa, Octa, Deca, Dodeca sound like one family while Octo pulls toward octopus and October. Octa, two to one. The page says she can overrule it. (By the same rule the d20 would be Icosa, not Icoso; open question 2.)
  - The sides: named by their number on the die, 1 to 8, until she chooses two more directions or keeps the numbers. Five candidate pairs are on the World tab, as she asked for at least three: Dawn and Dusk, Zenith and Nadir, Windward and Leeward, Over and Under, Sunward and Starward; and the corner-naming idea (Hexa's six directions are an octahedron's six corners) as a reading, offered, not used. Open question 1.
  - How the numbers sit: 1, 3, 5, 7 round the top corner, 1 facing the viewer at the start, going round to the viewer's left; opposite sides add up to 9, as on a d8. A reading (`OCTANTS`).
  - "the first side hasent been discoverd or drawn yet": every side is blank, side 1 carries her words on its card and in the Sides tab. Nothing else about Octa is written, so nothing else is drawn or claimed (no star, moon, fields, turn or calendar; the dock counts the shared clock's days).

### The second round, 2026-10-17, later: her answers to the first report

- 2026-10-17, Ruby: "1: give me another 5 so they arent confusing 2:witchever is the hedron name minus "hedron" 3: its great 4: yes it did 5: give octa the same star, a d7 moon, a turn, a calender with one more month than hexa and a restart day that is one and three fourths of a day pleese."
  - 1, the directions: five more pairs, plainer, on the World tab under the first five (Sunrise and Sunset, Light and Dark, Gold and Blue, Inner and Outer, Peak and Deep); none chosen, ten offered.
  - 2, the names: the rule for every planet is the hedron name minus "hedron". Octa stands (octahedron). The d20 is Icosa (icosahedron, Icoso until now) and the d24 Icositetra (icositetrahedron, Icosotetra until now) on all three World tabs; her 2026-10-10 list is quoted as she wrote it. The dwarf planets: a d2 is a dihedron, a d1 has no hedron; left to her (open question 4).
  - 3 and 4 are Hexa's: the shrink is "great" and the Far side shrank too, "yes it did" (recorded in `../cuba/HANDOFF.md`).
  - 5, the same star: Tetra's dark purple star, drawn where it stands (`SUN0`), lighting the sides; as large as from Hexa, since Octa's distance from it is unwritten.
  - 5, a d7 moon: a fair seven-faced die and no barrel, as the other moons (her 2026-10-04 and 2026-10-11 lines): a five-sided prism with five oblong sides (one to five craters) and two pentagon ends (six and seven), its half-length `MOON_PRISM` = 0.75 of the pentagon's side by the solid-angle rule (each face a seventh of the view; the shape and the proportion are readings). A third of Octa's size (`MOON_LEN`), and it keeps the other moons' ways (opposite the star, the eased swing through the star on the 14th of each month for an eclipse, rolling once a day, waxing and waning): a reading, she gave the die.
  - 5, a turn: one full turn a day, leftward, like Tetra and Hexa (`spinAngle`); the direction and the day's length are readings.
  - 5, the calendar: Hexa's fourteen months and one more, 15 of 28 days, and a Restart Day of 1.75 days after December: 421¾ days (`WORLD.calendar`). The fifteenth month is unnamed and sits after Amberary, between it and February (a reading); the HUD calls it "the unnamed month". The week's names are Tetra's (a reading); 420 month days are 60 weeks exactly. Years are not counted and no season is shown: unwritten.

## 3. Open questions for Ruby (do not guess these)

1. (2026-10-17) Two more directions to join Hexa's six, or keep the numbers? Ten pairs are offered on the World tab (five more after "give me another 5 so they arent confusing").
2. (Answered 2026-10-17: "witchever is the hedron name minus \"hedron\"": Icosa, Icositetra.)
3. (2026-10-17) Which number sits where on the die (the page's layout is a reading), and what the first side holds when it is discovered.
4. (Answered in part 2026-10-17: the same star, a d7 moon, a turn, a 15-month year with a 1¾-day Restart Day.) Still open: size, fields, seasons, how the years are counted, who goes there, where Octa sits among the worlds and how far from the star, whether it shows in Tetra's and Hexa's skies, the fifteenth month's name and place, the dwarf planets' names by the hedron rule.

## 4. Where it lives

`pipeline/world.html` (the fragment), `../tetra/pipeline/build.py` (inserts it at `{{OCTA}}`), `../tetra/tests/octa.js` (its test), `../tetra/dist/` (the shipped page). Ground rules in `CLAUDE.md`.

## 5. Publishing

- Draft 2, 2026-10-17: republished to Tetra's artifact with the label "v11 Octa turns under the star, a d7 moon, a 15-month year".
- Draft 1, 2026-10-17: republished to Tetra's artifact with the label "v11 Octa joins, eight blank sides; Hexa's lands shrunk".
