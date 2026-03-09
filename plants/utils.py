# plants/utils.py
import random

ARTIST_PLANT_MAP = {
    "bruno_mars": "sunflower",
    "tyler_the_creator": "lavender",
    "set_it_off": "cactus",
    "bear_ghost": "cactus",
}

PLANT_LEVEL_THRESHOLDS = {
    1: 0,
    2: 10,
    3: 50,
    4: 100,
    5: 200,
}

def to_artist_key(name):
    return name.lower().replace(" ", "_").replace("-", "_")

def get_plant_for_artist(artist_key):
    return ARTIST_PLANT_MAP.get(artist_key, None)

def get_plant_level(experience):
    level = 1
    for lvl, threshold in PLANT_LEVEL_THRESHOLDS.items():
        if experience >= threshold:
            level = lvl
    return level