import json
from dataclasses import dataclass
import random

import numpy as np
import sys
import os.path

# each faction gets up and downvotes. Chance of appearing is weighted by votes with exponential smoothing.

NUM_PLAYERS = 4

SMOOTHING = 0.5

CWD = os.path.abspath(os.path.dirname(sys.executable))
PATH = os.path.join(CWD, "content.json")

try:
    CONTENT = json.load(open(PATH, "r"))
except FileNotFoundError:
    print("not an exe")
    CONTENT = json.load(open("content.json", "r"))


@dataclass
class Item:
    name: str
    score: int


def get_items():
    items = []
    for dict_item in CONTENT:
        items.append(Item(name=dict_item["name"], score=dict_item["score"]))
    return items


def remove_type_matches(faction):
    faction_type = faction.get("type")
    if not faction_type:
        return

    for item in CONTENT["factions"]["red"]:
        if item.get("type") == faction_type:
            CONTENT["factions"]["red"].remove(item)
    for item in CONTENT["factions"]["grey"]:
        if item.get("type") == faction_type:
            CONTENT["factions"]["grey"].remove(item)


def get_weights(pool: list[dict]) -> list[float]:
    scores = [item["score"]/10 for item in pool]
    min_score = min(scores)  # to shift up to 0
    weights = [
        SMOOTHING * 0.5 + (1 - SMOOTHING) * (score - min_score) for score in scores
    ]
    weights = np.array(weights) / sum(weights)
    return weights


def draw_from_pool(pool: list[dict], num_to_draw=1):
    choices = []
    for draw in range(num_to_draw):
        weights = get_weights(pool)
        choice = np.random.choice(pool, p=weights)
        choices.append(choice)
        pool.remove(choice)

        remove_type_matches(choice)

    return choices


def main():
    _initial_red = draw_from_pool(CONTENT["factions"]["red"])
    _remaining = draw_from_pool(
        CONTENT["factions"]["red"] + CONTENT["factions"]["grey"],
        NUM_PLAYERS,
    )
    factions = _initial_red + _remaining

    for i, faction in enumerate(factions):
        if faction["name"].startswith("Vagabond"):
            vagabond = draw_from_pool(CONTENT["vagabonds"])[0]
            factions[i] = vagabond

    map_ = draw_from_pool(CONTENT["maps"])[0]

    deck = draw_from_pool(CONTENT["decks"])[0]

    print(", ".join([faction["name"] for faction in factions]))

    print(map_["name"])
    print(deck["name"])


if __name__ == "__main__":
    main()
    input("Press enter to exit")
