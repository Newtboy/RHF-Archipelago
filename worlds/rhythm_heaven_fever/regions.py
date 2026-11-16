
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from BaseClasses import MultiWorld, Region, Entrance

from .locations import (
    RHFLocation,
    ALL_LOCATION_TABLE,
    RANKS,
)
from .data import levels_dict, levels

if TYPE_CHECKING:
    from . import RhythmHeavenFeverWorld


def get_regions(world: RhythmHeavenFeverWorld):

    regions = {
        "Menu": [],
    }

    # Only include albums enabled by remix_count.
    selected_albums = list(levels_dict["core"].items())[
        :world.options.remix_count.value
    ]

    # Determine which Ranksanity ranks are enabled.
    if world.options.ranksanity.value:
        rank_cap = world.options.ranksanity_max_cap.value
        enabled_ranks = RANKS[:rank_cap]
    else:
        enabled_ranks = []

    # Levelsanity: Every individual level gets its own region.
    if world.options.levelsanity.value:

        selected_levels = levels[:world.options.remix_count.value * 5]

        for level_name in selected_levels:

            regions[level_name] = [level_name]

            # Determine whether this level is a remix.
            is_remix = level_name in levels_dict["core"]

            # Add Ranksanity locations.
            if enabled_ranks and (
                not is_remix
                or world.options.ranksanity_use_remixes.value
            ):
                regions[level_name].extend(
                    f"{level_name}: {rank}"
                    for rank in enabled_ranks
                )

    # Normal mode: All five levels belong to an album region.
    else:

        for album_index, (remix, album_levels) in enumerate(
            selected_albums
        ):

            region_name = f"Album {album_index + 1}"

            level_names = [remix, *album_levels]

            regions[region_name] = level_names.copy()

            # Add Ranksanity locations.
            if enabled_ranks:
                for level_name in level_names:

                    is_remix = level_name == remix

                    if is_remix and not world.options.ranksanity_use_remixes.value:
                        continue

                    regions[region_name].extend(
                        f"{level_name}: {rank}"
                        for rank in enabled_ranks
                    )

    return regions


def validate_regions(regions):

    assigned = Counter(
        location_name
        for location_names in regions.values()
        for location_name in location_names
    )

    # Check for locations that don't exist.
    for name in sorted(assigned.keys() - ALL_LOCATION_TABLE.keys()):
        print(f"UNKNOWN LOCATION: {name}")

    # Check for duplicate locations.
    for name, count in sorted(assigned.items()):
        if count > 1:
            print(f"DUPLICATE LOCATION ({count}x): {name}")


def create_regions(world: RhythmHeavenFeverWorld):

    player = world.player
    multiworld = world.multiworld

    regions = get_regions(world)

    validate_regions(regions)

    # Create all regions.
    for region_name in regions:

        region = Region(
            region_name,
            player,
            multiworld
        )

        multiworld.regions.append(region)

    # -------------------------------------------------------
    # CONNECTIONS
    # -------------------------------------------------------

    # Levelsanity: First five levels are free.
    if world.options.levelsanity.value:

        selected_levels = levels[:world.options.remix_count.value * 5]

        for level_index, level_name in enumerate(selected_levels):

            entrance = connect_regions(
                multiworld,
                player,
                "Menu",
                level_name
            )

            # First five levels need no unlock item.
            if level_index >= 5:
                entrance.access_rule = lambda state, name=level_name: (
                    state.has(f"{name} Unlock", player)
                )

    # Normal mode: Album 1 is free.
    else:

        for album_index in range(world.options.remix_count.value):

            album_name = f"Album {album_index + 1}"

            entrance = connect_regions(
                multiworld,
                player,
                "Menu",
                album_name
            )

            # Album 1 needs no unlock item.
            if album_index > 0:
                entrance.access_rule = lambda state, name=album_name: (
                    state.has(name, player)
                )

    # -------------------------------------------------------
    # ACTUAL LOCATION CREATION
    # -------------------------------------------------------

    for region_name, location_names in regions.items():

        region = multiworld.get_region(region_name, player)

        for location_name in location_names:

            location_id = ALL_LOCATION_TABLE[location_name]

            location = RHFLocation(
                player,
                location_name,
                location_id,
                region
            )

            region.locations.append(location)


def connect_regions(
    multiworld: MultiWorld,
    player: int,
    from_name: str,
    to_name: str,
    rule=None
) -> Entrance:

    source_region = multiworld.get_region(from_name, player)
    target_region = multiworld.get_region(to_name, player)

    entrance = source_region.connect(
        target_region,
        f"{from_name} -> {to_name}"
    )

    if rule is not None:
        entrance.access_rule = rule

    return entrance
