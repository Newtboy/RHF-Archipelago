from typing import *
from BaseClasses import Item, MultiWorld, Tutorial, ItemClassification, Region, Location, LocationProgressType
from worlds.AutoWorld import WebWorld, World
from .items import *
from .locations import *
from .options import *
from .regions import*
from .data import *
from .rules import *

class RhythmHeavenFeverWeb(WebWorld):
    theme = "partyTime"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Rhythm Heaven Fever randomizer connected to an Archipelago Multiworld.",
        "English",
        "setup_en.md",

        "setup/en",
        ["CallMeZero", "xMcacutt", "Beble"]
    )

    tutorials = [setup_en]
    option_groups = rhythm_heaven_fever_option_groups


class RhythmHeavenFeverWorld(World):
    """

    """
    game = "Rhythm Heaven Fever"
    rhythm_heaven_fever_world_version = "v1.0.0"
    options_dataclass = RhythmHeavenFeverOptions
    options: RhythmHeavenFeverOptions
    topology_present = True
    item_name_to_id = {**ALL_ITEM_TABLE}
    # location_name_to_id = {name: item.code for name, item in rhythm_heaven_fever_location_table.items()}
    location_name_to_id = {
        **ALL_LOCATION_TABLE
    }

    web = RhythmHeavenFeverWeb()

    def __init__(self, multiworld: MultiWorld, player: int):
        super().__init__(multiworld, player)
        self.item_pool = []


    def fill_slot_data(self) -> Mapping[str, Any]:
        #self.generate_puml()
        return {
            "Required Rank": self.options.required_rank.value,
            "Include Endless": self.options.include_endless.value,
            "Remix Count": self.options.remix_count.value,
            "Ranksanity": self.options.ranksanity.value,
            "Ranksanity Cap": self.options.ranksanity_max_cap.value,
            "Ranksanity Use Remixes": self.options.ranksanity_use_remixes.value,
            "Levelsanity": self.options.levelsanity.value,
        }

    def get_filler_item_name(self) -> str:
        return self.random.choice(list(JUNK_ITEM_IDS))

    def create_item(self, name: str) -> Item:
        if name in ALBUM_ITEM_IDS or name in LEVEL_ITEM_IDS:
            classification = ItemClassification.progression
        else:
            classification = ItemClassification.filler

        return RhythmHeavenFeverItem(
            name,
            classification,
            ALL_ITEM_TABLE[name],
            self.player
        )

    def create_items(self) -> None:
        self.create_item_pool()

    def create_item_pool(self) -> None:
        item_pool = []
        # Albums
        if (not self.options.levelsanity.value): # {
            for item in ALBUM_ITEM_IDS:
                item_pool.append(self.create_item(item))
        else:
            for item in LEVEL_ITEM_IDS:
                item_pool.append(self.create_item(item))

        # Fill remaining locations with junk
        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        remaining = total_locations - len(item_pool)

        for _ in range(remaining):
            item_pool.append(self.create_item(self.get_filler_item_name()))

        self.multiworld.itempool += item_pool

    # The part that ACTUALLY creates locations
    def create_regions(self):
        create_regions(self)

    def set_rules(self):
        rules.set_rules(self)

# =================================================================
# Launcher
# =================================================================

from worlds.LauncherComponents import (
    Component,
    components,
    Type,
    launch,
)


def launch_rhf_client(*args):
    from .client.launcher import run_client

    launch(
        run_client,
        name="Rhythm Heaven Fever Client",
        args=args,
    )


components.append(
    Component(
        "Rhythm Heaven Fever Client",
        func=launch_rhf_client,
        component_type=Type.CLIENT,
    )
)