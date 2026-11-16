from BaseClasses import Location
from .data import levels, levels_dict

GAME_NAME = "Rhythm Heaven Fever"

BASE_ID = 0x4C535700

EXTRA_LEVELS_IDS = {
	f"{levelName}":BASE_ID+1000+i
	for i, levelName in enumerate(levels_dict["extra"])
}

ENDLESS_LEVELS_IDS = {
	f"{levelName}":BASE_ID+2000+i
	for i, levelName in enumerate(levels_dict["endless"])
}

TOYS_LEVELS_IDS = {
	f"{levelName}":BASE_ID+3000+i
	for i, levelName in enumerate(levels_dict["toys"])
}

BASE_LEVEL_IDS = {
	f"{levelName}":BASE_ID+ 4000 + i
	for i, levelName in enumerate(levels)
} # only 50 levels

ranks = ["Try again.", "OK...", "Superb!", "Perfect!"]

RANKSANITY_LOCATION_IDS = {
    f"{levelName}: {rankname}": BASE_ID + 4500 + i * len(ranks) + rank_index
    for i, levelName in enumerate(levels)
    for rank_index, rankname in enumerate(ranks)
}


ALL_LOCATION_TABLE = {
	**EXTRA_LEVELS_IDS,
	**ENDLESS_LEVELS_IDS,
	**TOYS_LEVELS_IDS,
	**BASE_LEVEL_IDS,
	**RANKSANITY_LOCATION_IDS
}

class RHFLocation(Location):
	game = GAME_NAME