from BaseClasses import Location

from .data import levels, levels_dict


GAME_NAME = "Rhythm Heaven Fever"
BASE_ID = 0x52484600

RANKS = [
	"OK...",
	"Superb!",
	"Perfect!",
]


# Extra games (reserved for later)
EXTRA_LEVELS_IDS = {
	level_name: BASE_ID + 1000 + i
	for i, level_name in enumerate(levels_dict["extra"])
}

# Endless games (reserved for later)
ENDLESS_LEVELS_IDS = {
	level_name: BASE_ID + 2000 + i
	for i, level_name in enumerate(levels_dict["endless"])
}

# Rhythm toys (reserved for later)
TOYS_LEVELS_IDS = {
	level_name: BASE_ID + 3000 + i
	for i, level_name in enumerate(levels_dict["toys"])
}

# Main level completion locations
BASE_LEVEL_IDS = {
	level_name: BASE_ID + 4000 + i
	for i, level_name in enumerate(levels)
}

# Ranksanity locations
RANKSANITY_LOCATION_IDS = {
	f"{level_name}: {rank_name}": (
			BASE_ID + 4500 + i * len(RANKS) + rank_index
	)
	for i, level_name in enumerate(levels)
	for rank_index, rank_name in enumerate(RANKS)
}


ALL_LOCATION_TABLE = {
	**EXTRA_LEVELS_IDS,
	**ENDLESS_LEVELS_IDS,
	**TOYS_LEVELS_IDS,
	**BASE_LEVEL_IDS,
	**RANKSANITY_LOCATION_IDS,
}


class RHFLocation(Location):
	game = GAME_NAME
