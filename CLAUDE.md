# Cats (Oak & Sparrow Systems Enterprises)

Unrelated projects live in this repository. One rule covers all of them: no em dashes in any copy, code comment, doc or commit message (use commas, periods, parentheses, or restructure).

- `analyses/`: written anatomical analyses (feline). Markdown only, nothing to build.
- `cuba/`: Cuba, the cube planet, the second world of Ruby's Dice System: its map generator and the page fragment that Tetra's build inserts (Ruby: one file with Tetra). Tetra's rules apply; read `cuba/CLAUDE.md`, then `cuba/HANDOFF.md`. `make maps` and `make audit` run inside `cuba/`; the page is built, tested and shipped from `tetra/`.
- `tetra/`: Tetra, Ruby's four-sided world: the map pipeline, the page template, the Playwright checks and the shipped build. **Read `tetra/CLAUDE.md` first** (ground rules, layout, geometry conventions, how a round from Ruby is processed), then `tetra/HANDOFF.md` (state, canon ledger, open questions). Run its `make` targets from inside `tetra/`.
