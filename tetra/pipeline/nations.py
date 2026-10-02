"""Where the island and continent nations sit, as texture-pixel offsets from the island / continent centre.
Shared by mapgen2.py (Codex crop labels) and build.py (markers), so the two always agree.
Spellings per Ruby: Marshia, Baiuland, Greeneria."""
ISLAND_NATIONS = [   # id, name, (dx, dy) from the central island's centre, unsure spelling?
    ('swampland', 'Swampland', (-38, -72), False),
    ('greenia', 'Greenia', (-52, -14), False),
    ('marshia', 'Marshia', (-44, 48), False),
    ('greeneria', 'Greeneria', (28, 74), False),
    ('baiuland', 'Baiuland', (60, 8), False),
]
CONTINENT_NATIONS = [
    ('snowia', 'Snowia', (-20, -100), False),
    ('coldland', 'Coldland', (-95, 20), False),
    ('beria', 'Beria', (55, 80), False),
]
