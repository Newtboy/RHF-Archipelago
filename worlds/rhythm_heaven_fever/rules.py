import typing

from rule_builder.rules import True_, Has, HasAllCounts

from . import data
if (typing.TYPE_CHECKING): # {
	from . import RhythmHeavenFeverWorld


def set_rules(world: "RhythmHeavenFeverWorld"):
	player = world.player

	RANKS = ["OK...", "Superb!", "Perfect!"]
	ranks = RANKS[:world.options.ranksanity_max_cap.value]

	# SELECTED LEVELS
	selected_albums = list(data.levels_dict["core"].items())[
		:world.options.remix_count.value
	]

	selected_levels = [
		level
		for remix, album_levels in selected_albums
		for level in [remix, *album_levels]
	]

	# LEVELSANITY
	if world.options.levelsanity.value:
		selected_levels = data.levels

		for index, level in enumerate(selected_levels): # {
			if (index < 5): # {
				continue
			# }
			else: # {
				rule = Has("{level} Unlock")

				world.multiworld.get_location(
					level, player
				).access_rule = rule.resolve(world)
			# }
			if world.options.ranksanity.value:
				for rank in ranks:
					world.multiworld.get_location(
						f"{level}: {rank}", player
					).access_rule = (rule if world.options.ranksanity_use_remixes.value else True_()).resolve(world)

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
	required_rank_locations = []

	if world.options.ranksanity.value:
		required_rank = ranks[-1]

		for level in selected_levels:
			is_remix = level in data.levels_dict["core"]

			if is_remix and not world.options.ranksanity_use_remixes.value:
				continue

			required_rank_locations.append(
				f"{level}: {required_rank}"
			)

	else:
		required_rank = RANKS[world.options.required_rank.value]

		required_rank_locations = [
			f"{level}: {required_rank}"
			for level in selected_levels
		]