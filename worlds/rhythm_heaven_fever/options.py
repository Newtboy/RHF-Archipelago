from dataclasses import dataclass

from Options import Choice, Range, Toggle, DeathLink, DefaultOnToggle, OptionGroup, PerGameCommonOptions, OptionSet


class RequiredRank(Choice):
    """
    The rank required to receive a check on a level.

    OK: Any passing rank will reward a check

    Superb: Better than OK, while still allowing a few misses

    Does not apply when Ranksanity is enabled
    """
    display_name = "Required Rank"
    option_ok = 0
    option_superb = 1
    default = 1

class Ranksanity(Toggle): # {
    """Use ranksanity"""
    display_name = "Ranksanity"
    default = Toggle.option_false

class RanksanityUseRemixes(Toggle): # {
    """Allow ranksanity to affect remixes"""
    display_name = "Remixes in ranksanity?"
    default = Toggle.option_false

class RanksanityMaxCap(Choice): # {
    """The highest check level for ranksanity"""
    display_name = "Ranksanity Cap"
    option_perfect = 3
    option_superb = 2
    option_ok = 1
    default = 2

class Levelsanity(Toggle): # {
    """Randomize *every* level"""
    display_name="Levelsanity"
    default = Toggle.option_false

class IncludeEndless(Toggle):
    """
    Adds endless games to the pool.
    Each endless game has a high score that must be reached to send a check.
    """
    display_name = "Include Endless"


class RemixCount(Range):
    """
    Number of remixes before goal. (Reduces total number of levels to be played).
    This becomes number of levels before goal (remix count * 5)
    """
    display_name = "Remix Count"
    range_start = 4
    range_end = 10
    default = 5


rhythm_heaven_fever_option_groups = [
    OptionGroup("Core", [
        RequiredRank,
        RemixCount,
        IncludeEndless
    ]),
    OptionGroup("Sanities", [
        Ranksanity, RanksanityMaxCap, RanksanityUseRemixes, Levelsanity
    ])
]


@dataclass
class RhythmHeavenFeverOptions(PerGameCommonOptions):
    required_rank: RequiredRank
    ranksanity: Ranksanity
    ranksanity_max_cap: RanksanityMaxCap
    ranksanity_use_remixes: RanksanityUseRemixes
    levelsanity: Levelsanity
    remix_count: RemixCount
    include_endless: IncludeEndless
