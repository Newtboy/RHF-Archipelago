import asyncio
import CommonClient
import dolphin_memory_engine as dme

import worlds.rhythm_heaven_fever
from worlds.rhythm_heaven_fever.client.RHFEnums import LevelCompletion
from worlds.rhythm_heaven_fever.client.RHFMemory import (
	RHFMemoryEditor,
	RHFMemory,
)


class RHFClient(CommonClient.CommonContext):
	game = "Rhythm Heaven Fever"
	items_handling = 0b111

	def __init__(self, server_address, password):
		super().__init__(server_address, password)

		self.memory_editor = None
		self.game_memory = None
		self.game_watcher_task = None

		self.goal_sent = False

		self.level_state = {}
		self.sent_locations = set()

	async def server_auth(self, password_requested=False):
		await super().server_auth(password_requested)

		if not dme.is_hooked():
			dme.hook()

		if not dme.is_hooked():
			raise ConnectionResetError(
				"Make sure Dolphin is running."
			)

		# TODO: Ask for slot number

		self.memory_editor = RHFMemoryEditor(slotnum=1)
		self.game_memory = RHFMemory(self)

		self.memory_editor.show_all_cols()

		await self.get_username()
		await self.send_connect()

	def initialize_level_access(self):
		levels = worlds.rhythm_heaven_fever.levels

		# First five levels are always available.
		for level in levels[:5]:
			self.memory_editor.unlockLevel(level)

		# Remaining levels depend on received AP items.
		for level in levels[5:]:
			if self.game_memory.level_state[level]["ap_received"]:
				self.memory_editor.unlockLevel(level)
			else:
				self.memory_editor.lockLevel(level)

		print("[RHF] Level access initialized.")

	async def game_watcher(self):
		print("[RHF Watcher] Started.")

		# Unlock the starting five levels.
		# Existing completion ranks are preserved.
		for level in worlds.rhythm_heaven_fever.levels[:5]:
			self.memory_editor.unlockLevel(level)
		self.initialize_level_access()

		while True:
			try:
				if not dme.is_hooked():
					raise ConnectionResetError(
						"Dolphin disconnected."
					)

				await self.check_levels()
				await asyncio.sleep(0.5)

			except Exception:
				import traceback
				traceback.print_exc()
				raise

	async def check_levels(self):
		gameState = self.memory_editor.getLevelStatesFromGame()

		for level in worlds.rhythm_heaven_fever.levels:
			if level not in gameState:
				continue

			achieved_rank = gameState[level]
			previous_rank = self.game_memory.level_state[level]["highest_rank"]

			if achieved_rank > previous_rank:
				print(
					f"[RHF Rank] {level}: "
					f"{previous_rank.name} -> {achieved_rank.name}"
				)

				self.game_memory.level_state[level]["highest_rank"] = achieved_rank

				self.update_next_level(level)

			else:
				achieved_rank = previous_rank

			if not self.ranksanity:
				required_rank = (
					LevelCompletion.OK
					if self.requiredRank == 0
					else LevelCompletion.SUPERB
				)

				if achieved_rank >= required_rank:
					await self.sendLevelCheck(level)

			else:
				await self.check_ranksanity(
					level,
					achieved_rank
				)

	async def check_ranksanity(self, level: str, achieved_rank):

		for rank_name in self.ranks:

			rank_value = {
				"OK...": LevelCompletion.OK,
				"Superb!": LevelCompletion.SUPERB,
				"Perfect!": LevelCompletion.PERFECT,
			}[rank_name]

			if achieved_rank >= rank_value:
				await self.sendRanksanityCheck(
					level,
					rank_name
				)

	async def sendLevelCheck(self, name: str):
		location_id = worlds.rhythm_heaven_fever.BASE_LEVEL_IDS[name]

		if location_id in self.sent_locations:
			return

		print(f"[RHF Check] Sending: {name}")

		await self.send_msgs([{
			"cmd": "LocationChecks",
			"locations": [location_id],
		}])

		self.sent_locations.add(location_id)

	def update_next_level(self, current_level):
		levels = worlds.rhythm_heaven_fever.levels

		current_index = levels.index(current_level)

		# Ignore the first five levels.
		if current_index < 5:
			return

		next_index = current_index + 1

		if next_index >= len(levels):
			return

		next_level = levels[next_index]

		if self.game_memory.level_state[next_level]["ap_received"]:
			return

		self.memory_editor.lockLevel(next_level)

		print(
			f"[RHF Progression] Locked {next_level}: "
			"AP item not received."
		)

	async def sendRanksanityCheck(self, name: str, rank: str):
		location_name = f"{name}: {rank}"

		location_id = worlds.rhythm_heaven_fever.RANKSANITY_LOCATION_IDS[
			location_name
		]

		if location_id in self.sent_locations:
			return

		print(f"[RHF Check] Sending: {location_name}")

		await self.send_msgs([{
			"cmd": "LocationChecks",
			"locations": [location_id],
		}])

		self.sent_locations.add(location_id)

	def on_package(self, cmd: str, args: dict):
		if not dme.is_hooked():
			raise ConnectionResetError(
				"Dolphin disconnected."
			)

		if cmd == "Connected":
			self.ranksanity = args["slot_data"]["Ranksanity"]
			self.ranksanityCap = args["slot_data"]["Ranksanity Cap"]
			self.ranksanityRemixes = args["slot_data"]["Ranksanity Use Remixes"]
			self.levelsanity = args["slot_data"]["Levelsanity"]
			if (not self.ranksanity):  # {
				# Don't bother making this if ranksanity is enabled, bugs show up nicer if it crashes :)
				self.requiredRank = args["slot_data"]["Required Rank"]
			self.useEndless = args["slot_data"]["Include Endless"]
			self.remixCount = args["slot_data"]["Remix Count"]

			if self.game_watcher_task is None:
				self.game_watcher_task = asyncio.create_task(
					self.game_watcher()
				)

			RANKS = ["OK...", "Superb!", "Perfect!"]
			self.ranks = RANKS[:self.ranksanityCap]

		elif cmd == "ReceivedItems":
			for item in args["items"]:
				asyncio.create_task(
					self.handle_received_item(item)
				)

		super().on_package(cmd, args)

	async def handle_received_item(self, item):
		if self.game_memory is None:
			return

		if not self.levelsanity:
			for name, item_id in worlds.rhythm_heaven_fever.ALBUM_ITEM_IDS.items():
				if item.item == item_id:
					album_number = int(
						name.removeprefix("Album ")
					)
					self.memory_editor.unlockAlbum(album_number)
					return

		else:
			for name, item_id in worlds.rhythm_heaven_fever.LEVEL_ITEM_IDS.items():
				if item.item == item_id:
					level_name = name.removesuffix(" Unlock")

					self.game_memory.level_state[level_name]["ap_received"] = True

					self.memory_editor.unlockLevel(level_name)

					return

# Location detection methods go here.
# Item application methods go here.
