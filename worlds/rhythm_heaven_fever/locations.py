from BaseClasses import Location
from .data import levels, levels_dict

GAME_NAME = "Rhythm Heaven Fever"

BASE_ID = 0x4C535700

EXTRA_LEVELS_IDS = {
	f"{levelName}":1000+i
	for i, levelName in enumerate(levels_dict["extra"])
}

ENDLESS_LEVELS_IDS = {
	f"{levelName}":2000+i
	for i, levelName in enumerate(levels_dict["extra"])
}

TOYS_LEVELS_IDS = {
	f"{levelName}":3000+i
	for i, levelName in enumerate(levels_dict["extra"])
}

BASE_LEVEL_IDS = {
	f"{levelName}": 4000 + i
	for i, levelName in enumerate(levels)
} # only 50 levels

RANKSANITY_LOCATION_IDS:dict[str, int] = {}
ranks = ["Try again.", "OK...", "Superb!", "Perfect!"]
for i, levelName in enumerate(levels): # {
	for i, rankname in enumerate(ranks): # {
		RANKSANITY_LOCATION_IDS[f"{levelName}: {rankname}"] = 4500 + i


ALL_LOCATION_TABLE = {
	**EXTRA_LEVELS_IDS,
	**BASE_LEVEL_IDS,
	**RANKSANITY_LOCATION_IDS
}

class RHFLocation(Location):
	game = GAME_NAME