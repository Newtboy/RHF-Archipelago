from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from BaseClasses import MultiWorld, Region, Entrance

from .locations import (
	RHFLocation,
	ALL_LOCATION_TABLE,
	RANKS,
	EXTRA_LEVELS_IDS,
	ENDLESS_LEVELS_IDS,
	TOYS_LEVELS_IDS,
)

from .data import levels_dict, levels

if TYPE_CHECKING:
	from . import RhythmHeavenFeverWorld

# -------------------------------------------------------
# LOCATION LISTS
# -------------------------------------------------------

menu = (
		# list(EXTRA_LEVELS_IDS)
		# + list(ENDLESS_LEVELS_IDS)
		# + list(TOYS_LEVELS_IDS)
	list()
)


# -------------------------------------------------------
# REGION DEFINITIONS
# -------------------------------------------------------

def get_regions(world: RhythmHeavenFeverWorld):
	regions = {
		"Menu": menu.copy(),
	}

	selected_albums = list(levels_dict["core"].items())

	# Determine which Ranksanity ranks are enabled.
	if world.options.ranksanity.value:
		rank_cap = world.options.ranksanity_max_cap.value
		enabled_ranks = RANKS[:rank_cap]
	else:
		enabled_ranks = []

	# -------------------------------------------------------
	# LEVELSANITY
	# -------------------------------------------------------
	if world.options.levelsanity.value:
		for level_name in levels:
			regions[level_name] = [level_name]

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

	# -------------------------------------------------------
	# NORMAL ALBUM MODE
	# -------------------------------------------------------
	else:
		for album_index, (remix, album_levels) in enumerate(
			selected_albums
		):
			album_name = f"Album {album_index + 1}"
			level_names = [remix, *album_levels]

			regions[album_name] = level_names.copy()

			# Add Ranksanity locations.
			if enabled_ranks:
				for level_name in level_names:
					is_remix = level_name == remix

					if (
						is_remix
						and not world.options.ranksanity_use_remixes.value
					):
						continue

					regions[album_name].extend(
						f"{level_name}: {rank}"
						for rank in enabled_ranks
					)

	return regions

# -------------------------------------------------------
# VALIDATION
# -------------------------------------------------------

def validate_regions(regions):
	assigned = Counter(
		location_name
		for location_names in regions.values()
		for location_name in location_names
	)

	# Locations that don't exist in locations.py.
	for name in sorted(
			assigned.keys() - ALL_LOCATION_TABLE.keys()
	):
		print(f"UNKNOWN LOCATION: {name}")

	# Locations accidentally assigned more than once.
	for name, count in sorted(assigned.items()):
		if count > 1:
			print(f"DUPLICATE LOCATION ({count}x): {name}")


# -------------------------------------------------------
# REGION CREATION
# -------------------------------------------------------

def create_regions(world: RhythmHeavenFeverWorld):
	player = world.player
	multiworld = world.multiworld

	regions = get_regions(world)

	validate_regions(regions)

	# -------------------------------------------------------
	# CREATE REGIONS
	# -------------------------------------------------------

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

	# LEVELSANITY
	if world.options.levelsanity.value:

		selected_levels = levels

		for level_index, level_name in enumerate(selected_levels):

			entrance = connect_regions(
				multiworld,
				player,
				"Menu",
				level_name
			)

			# First five levels are free.
			if level_index >= 5:
				entrance.access_rule = lambda state, name=level_name: (
					state.has(f"{name} Unlock", player)
				)

	# NORMAL ALBUM MODE
	else:
		for album_index, (remix, album_levels) in enumerate(
				levels_dict["core"].items()
		):
			album_name = f"Album {album_index + 1}"

			entrance = connect_regions(
				multiworld,
				player,
				"Menu",
				album_name
			)

			# First album is free.
			if album_index >= 1:
				entrance.access_rule = lambda state, name=album_name: (
					state.has(name, player)
				)

	# -------------------------------------------------------
	# ASSIGN LOCATIONS TO REGIONS
	# -------------------------------------------------------

	for region_name, location_names in regions.items():

		region = multiworld.get_region(region_name, player)

		for location_name in location_names:
			location_id = ALL_LOCATION_TABLE[location_name]

			region.locations.append(
				RHFLocation(
					player,
					location_name,
					location_id,
					region
				)
			)


# -------------------------------------------------------
# CONNECTION HELPERS
# -------------------------------------------------------

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
