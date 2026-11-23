import typing

from .locations import ALL_LOCATION_TABLE
from rule_builder.rules import True_, Has, HasAllCounts

from . import data
if (typing.TYPE_CHECKING): # {
	from . import RhythmHeavenFeverWorld


def set_rules(world: "RhythmHeavenFeverWorld"):
	player = world.player

	RANKS = ["OK...", "Superb!", "Perfect!"]
	ranks = RANKS[:world.options.ranksanity_max_cap.value]

	# SELECTED LEVELS
	selected_albums = list(data.levels_dict["core"].items())

	selected_levels = [
		level
		for remix, album_levels in selected_albums
		for level in [remix, *album_levels]
	]

	# LEVELSANITY
	if world.options.levelsanity.value:
		selected_levels = data.levels

		for index, level in enumerate(selected_levels):
			is_remix = level in data.levels_dict["core"]

			if index < 5:
				rule = True_()
			else:
				rule = Has(f"{level} Unlock")

			world.multiworld.get_location(
				level, player
			).access_rule = rule.resolve(world)

			if world.options.ranksanity.value and (not is_remix or world.options.ranksanity_use_remixes.value):
				for rank in ranks:
					world.multiworld.get_location(f"{level}: {rank}", player).access_rule = rule.resolve(world)

	# ALBUM PROGRESSION
	else:
		for album_index, (remix, album_levels) in enumerate(selected_albums):
			if album_index == 0:
				continue

			rule = HasAllCounts(
				{f"Album {album_index + 1}": 1}
			).resolve(world)

			for level in [remix, *album_levels]:
				world.multiworld.get_location(
					level, player
			).access_rule = rule

	# GOAL
	required_rank = RANKS[
		min(
			world.options.required_rank.value,
			world.options.ranksanity_max_cap.value - 1
		)
	]

	if world.options.ranksanity.value:
		goal_locations = [
			location_name
			for location_name in ALL_LOCATION_TABLE
			if location_name.endswith(f": {required_rank}")
			   and (
					   world.options.ranksanity_use_remixes.value
					   or location_name.rsplit(": ", 1)[0]
					   not in data.levels_dict["core"]
			   )
		]
	else:
		goal_locations = selected_levels.copy()

	# Exclude free content from the goal.
	if world.options.levelsanity.value:
		goal_locations = [
			location_name
			for location_name in goal_locations
			if selected_levels.index(
				location_name.split(": ", 1)[0]
			) >= 5
		]
	else:
		goal_locations = [
			location_name
			for location_name in goal_locations
			if location_name not in data.levels_dict["core"].get(
				list(data.levels_dict["core"])[0], []
			)
			   and location_name != list(data.levels_dict["core"])[0]
		]

	needed = min(
		world.options.remix_count.value*5,
		len(goal_locations)
	)
	# DEBUG: Verify goal locations exist.
	for location_name in goal_locations:
		try:
			world.multiworld.get_location(location_name, player)
		except KeyError:
			print(
				f"MISSING GOAL LOCATION: {location_name} "
				f"(Ranksanity={world.options.ranksanity.value}, "
				f"Remixes={world.options.ranksanity_use_remixes.value}, "
				f"Levelsanity={world.options.levelsanity.value})"
			)
	world.multiworld.completion_condition[player] = (
		lambda state: sum(
			state.can_reach_location(location_name, player)
			for location_name in goal_locations
		) >= needed
	)