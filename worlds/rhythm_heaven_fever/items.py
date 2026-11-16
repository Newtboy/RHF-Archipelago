
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

from .data import levels, levels_dict, BOOK, MUSIC

if TYPE_CHECKING:
    from . import RhythmHeavenFeverWorld


GAME_NAME = "Rhythm Heaven Fever"
BASE_ID = 0x52484600


class RhythmHeavenFeverItem(Item):
    game = GAME_NAME


@dataclass(frozen=True)
class ItemData:
    code: int
    classification: ItemClassification


def generate_item_table() -> dict[str, ItemData]:
    item_table = {}

    # Album unlocks: Album 2 through Album 10
    for album_index in range(1, 10):
        item_table[f"Album {album_index + 1}"] = ItemData(
            BASE_ID + album_index,
            ItemClassification.progression
        )

    # Individual level unlocks
    for i, level in enumerate(levels):
        item_table[f"{level} Unlock"] = ItemData(
            BASE_ID + 100 + i,
            ItemClassification.progression
        )

    # Rhythm toys (reserved for later)
    for i, toy in enumerate(levels_dict["toys"]):
        item_table[f"{toy} Toy"] = ItemData(
            BASE_ID + 200 + i,
            ItemClassification.filler
        )

    # Endless games (reserved for later)
    for i, endless_game in enumerate(levels_dict["endless"]):
        item_table[f"Endless Game - {endless_game}"] = ItemData(
            BASE_ID + 300 + i,
            ItemClassification.filler
        )

    # Extra games (reserved for later)
    for i, extra_game in enumerate(levels_dict["extra"]):
        item_table[f"Extra Game - {extra_game}"] = ItemData(
            BASE_ID + 400 + i,
            ItemClassification.filler
        )

    # Junk items
    item_table[f"Random {MUSIC}"] = ItemData(
        BASE_ID + 500,
        ItemClassification.filler
    )

    item_table[f"Random {BOOK}"] = ItemData(
        BASE_ID + 501,
        ItemClassification.filler
    )

    return item_table


rhythm_heaven_fever_item_table = generate_item_table()


def get_random_item_names(rand, k: int, weights: dict[str, int]) -> list[str]:
    return rand.choices(
        list(weights.keys()),
        weights=list(weights.values()),
        k=k
    )


def create_single(
    name: str,
    world: RhythmHeavenFeverWorld,
    item_class: ItemClassification | None = None
) -> None:
    item_data = rhythm_heaven_fever_item_table[name]

    classification = (
        item_data.classification
        if item_class is None
        else item_class
    )

    world.item_pool.append(
        RhythmHeavenFeverItem(
            name,
            classification,
            item_data.code,
            world.player
        )
    )


def create_items(world: RhythmHeavenFeverWorld):
    total_location_count = len(
        world.multiworld.get_unfilled_locations(world.player)
    )

    # Album progression (normal mode)
    if not world.options.levelsanity.value:
        for album_index in range(1, world.options.remix_count.value):
            create_single(f"Album {album_index + 1}", world)

    # Individual level progression (Levelsanity)
    else:
        enabled_levels = levels[:world.options.remix_count.value * 5]

        # First five levels are available at the start
        for level in enabled_levels[5:]:
            create_single(f"{level} Unlock", world)

    # Junk
    junk_count = total_location_count - len(world.item_pool)

    if junk_count < 0:
        raise ValueError(
            f"Too many items! {len(world.item_pool)} items for "
            f"{total_location_count} locations."
        )

    junk_weights = {
        f"Random {BOOK}": 50,
        f"Random {MUSIC}": 50
    }

    junk = get_random_item_names(
        world.random,
        junk_count,
        junk_weights
    )

    for name in junk:
        create_single(name, world)

    world.multiworld.itempool += world.item_pool
