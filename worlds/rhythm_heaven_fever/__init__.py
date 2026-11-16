import copy
import typing
from typing import *
from BaseClasses import Item, MultiWorld, Tutorial, ItemClassification, Region, Location, LocationProgressType
from Options import OptionError, Accessibility
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
    item_name_to_id = {name: item.code for name, item in rhythm_heaven_fever_item_table.items()}
    # location_name_to_id = {name: item.code for name, item in rhythm_heaven_fever_location_table.items()}
    location_name_to_id = {
        **ALL_LOCATION_TABLE
    }
    if (options.levelsanity.value): # {
        pass

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
        return get_random_item_names(self.random, 1, junk_weights)[0]

    def generate_early(self) -> None:
        self.handle_ut_yamless(None)

    def create_item(self, name: str) -> Item:
        item_info = rhythm_heaven_fever_item_table[name]
        return RhythmHeavenFeverItem(name, item_info.classification, item_info.code, self.player)

    def create_items(self):
        create_items(self)

    # The part that ACTUALLY creates locations
    def create_regions(self):
        create_regions(self)

    def set_rules(self):
        for extra_game in levels_dict["extra"]:
            loc = self.get_location(f"{extra_game}")
            loc.access_rule = lambda state, game=extra_game: state.has(f"Extra Game - {extra_game}", self.player)
        self.multiworld.completion_condition[self.player] \
            = lambda state: state.can_reach_location(f"Remix {self.options.remix_count}", self.player)