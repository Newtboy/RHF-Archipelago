from __future__ import annotations

from BaseClasses import Item, ItemClassification

from .data import levels, levels_dict, BOOK, MUSIC


GAME_NAME = "Rhythm Heaven Fever"

BASE_ID = 0x52484600


class RhythmHeavenFeverItem(Item):
    game = GAME_NAME


# Albums
ALBUM_ITEM_IDS = {
    f"Album {i + 1}": BASE_ID + i
    for i in range(2, 11)
}

# Individual Levels
LEVEL_ITEM_IDS = {
    f"{level} Unlock": BASE_ID + 100 + i
    for i, level in enumerate(levels)
}

# Rhythm Toys (NYI)
TOY_ITEM_IDS = {
    f"{toy} Toy": BASE_ID + 200 + i
    for i, toy in enumerate(levels_dict["toys"])
}

# Endless Games (NYI)
ENDLESS_ITEM_IDS = {
    f"Endless Game - {game}": BASE_ID + 300 + i
    for i, game in enumerate(levels_dict["endless"])
}

# Extra Games (NYI)
EXTRA_ITEM_IDS = {
    f"Extra Game - {game}": BASE_ID + 400 + i
    for i, game in enumerate(levels_dict["extra"])
}

# Junk
JUNK_ITEM_IDS = {
    f"Random {MUSIC}": BASE_ID + 500,
    f"Random {BOOK}": BASE_ID + 501
}


# Item Classifications
ALBUM_ITEM_CLASSIFICATION = ItemClassification.progression
LEVEL_ITEM_CLASSIFICATION = ItemClassification.progression

TOY_ITEM_CLASSIFICATION = ItemClassification.filler
ENDLESS_ITEM_CLASSIFICATION = ItemClassification.filler
EXTRA_ITEM_CLASSIFICATION = ItemClassification.filler

JUNK_ITEM_CLASSIFICATION = ItemClassification.filler