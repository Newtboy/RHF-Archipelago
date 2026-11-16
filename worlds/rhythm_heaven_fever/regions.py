from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from BaseClasses import MultiWorld, Region, Entrance

from .locations import RHFLocation, ALL_LOCATION_TABLE
from .data import levels_dict, TOYS, ENDLESS

if TYPE_CHECKING:
    from . import RhythmHeavenFeverWorld


# ---------------------------------------------------------------------------
# REGION DEFINITIONS
# ---------------------------------------------------------------------------

RANKS = [
    "Try again.",
    "OK...",
    "Superb!",
    "Perfect!",
]


def get_regions(world: RhythmHeavenFeverWorld):

    regions = {
        "Menu": [],
        "Extra Games": levels_dict["extra"],
        TOYS: levels_dict["toys"],
    }

    # Endless Games
    if world.options.include_endless.value:
        regions[ENDLESS] = levels_dict["endless"]

    # Select the albums included in this seed.
    selected_albums = list(levels_dict["core"].items())[
        :world.options.remix_count.value
    ]

    # Levelsanity: Every individual game becomes its own region.
    if world.options.levelsanity.value:

        for remix, album_levels in selected_albums:

            for level_name in [remix, *album_levels]:

                regions[level_name] = [level_name]

                # Ranksanity
                if world.options.ranksanity.value:
                    regions[level_name].extend(
                        f"{level_name}: {rank}"
                        for rank in RANKS
                    )

    # Normal mode: Games are grouped into albums.
    else:

        for album_index, (remix, album_levels) in enumerate(
            selected_albums
        ):

            region_name = f"Album {album_index + 1}"

            regions[region_name] = [
                *album_levels,
                remix,
            ]

            # Ranksanity
            if world.options.ranksanity.value:
                regions[region_name].extend(
                    f"{level_name}: {rank}"
                    for level_name in [*album_levels, remix]
                    for rank in RANKS
                )

    return regions


# ---------------------------------------------------------------------------
# REGION VALIDATION
# ---------------------------------------------------------------------------

def validate_regions(regions):

    assigned = Counter(
        location_name
        for location_names in regions.values()
        for location_name in location_names
    )

    # Locations that don't exist in ALL_LOCATION_TABLE
    for name in sorted(assigned.keys() - ALL_LOCATION_TABLE.keys()):
        print(f"UNKNOWN LOCATION: {name}")

    # Locations assigned more than once
    for name, count in sorted(assigned.items()):
        if count > 1:
            print(f"DUPLICATE LOCATION ({count}x): {name}")

    # Locations not assigned to a region
    for name in sorted(ALL_LOCATION_TABLE.keys() - assigned.keys()):
        print(f"UNASSIGNED LOCATION: {name}")


# ---------------------------------------------------------------------------
# REGION CREATION
# ---------------------------------------------------------------------------

def create_regions(world: RhythmHeavenFeverWorld):

    player = world.player
    multiworld = world.multiworld

    regions = get_regions(world)

    validate_regions(regions)

    # Create all regions
    for region_name in regions:

        region = Region(
            region_name,
            player,
            multiworld
        )

        multiworld.regions.append(region)

    # -----------------------------------------------------------------------
    # CONNECTIONS
    # -----------------------------------------------------------------------

    # Extra Games
    connect_regions(multiworld, player, "Menu", "Extra Games")

    # Rhythm Toys
    connect_regions(multiworld, player, "Menu", TOYS)

    # Endless Games
    if world.options.include_endless.value:
        connect_regions(multiworld, player, "Menu", ENDLESS)

    # Levelsanity connections
    if world.options.levelsanity.value:

        selected_albums = list(levels_dict["core"].items())[
            :world.options.remix_count.value
        ]

        for remix, album_levels in selected_albums:

            for level_name in [remix, *album_levels]:

                connect_regions(
                    multiworld,
                    player,
                    "Menu",
                    level_name
                )

    # Normal album connections
    else:

        if world.options.remix_count.value > 0:

            connect_regions(
                multiworld,
                player,
                "Menu",
                "Album 1"
            )

        for album_index in range(
            1,
            world.options.remix_count.value
        ):

            entrance = connect_regions(
                multiworld,
                player,
                f"Album {album_index}",
                f"Album {album_index + 1}"
            )

            entrance.access_rule = lambda state, album=album_index: (
                state.has(f"Album {album + 1}", player)
            )

    # -----------------------------------------------------------------------
    # ACTUAL LOCATION CREATION
    # -----------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# CONNECTION HELPERS
# ---------------------------------------------------------------------------

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


def connect_bidirectional(
    multiworld: MultiWorld,
    player: int,
    a: str,
    b: str,
    rule=None,
    return_rule=None
):

    connect_regions(multiworld, player, a, b, rule)
    connect_regions(multiworld, player, b, a, return_rule)
