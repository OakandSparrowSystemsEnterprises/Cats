# Tetra

Ruby's four-sided world, as an interactive page. `dist/tetra_world.html` is the shipped build (version 10); open it in any browser, no server needed.

Start with `CLAUDE.md` (rules, layout, conventions) and `HANDOFF.md` (state, canon ledger, open questions).

## Quickstart

```
pip install -r requirements.txt
npm install && npx playwright install chromium

make maps     # regenerate the West, South and Far maps (deterministic)
make check    # edge agreement between faces
make build    # dist/tetra.html + dist/tetra_world.html
make test     # Playwright: smoke, walkthrough, phases, tap
make seams    # screenshots of the six shared edges, in tests/out/
make audit    # em dashes, retired names, placeholders
```

`make all` runs maps, build, test and audit. On Windows without `make`, run the commands inside the Makefile by hand; every script is plain Python 3 or Node.
