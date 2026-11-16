import asyncio
import enum
from enum import Enum

import CommonClient
import dolphin_memory_engine as dme

import worlds.rhythm_heaven_fever
from worlds.rhythm_heaven_fever.client.RHFMemory import RHFMemoryEditor, RHFMemory


class LevelCompletion(Enum):
	NOTRECEIVED = 0
	TRYAGAIN = 1
	OK = 2
	SUPERB = 3
	PERFECT = 4

class RHFClient(CommonClient.CommonContext):

	game = "Rhythm Heaven Fever"
	items_handling = 0b111

	def __init__(self, server_address, password):
		super().__init__(server_address, password)

		self.game_memory = None
		self.game_watcher_task = None

		self.goal_sent = False

		self.level_state = {}


	async def server_auth(self, password_requested=False):
		await super().server_auth(password_requested)

		if not dme.is_hooked():
			dme.hook()

		if not dme.is_hooked():
			raise ConnectionResetError(
				"Make sure Dolphin is running."
			)

		self.memory_editor = RHFMemoryEditor()
		self.game_memory = RHFMemory()

		self.initialize_game_state()

		if self.game_watcher_task is None:
			self.game_watcher_task = asyncio.create_task(
				self.game_watcher()
			)

		self.memory_editor.show_all_cols()

		await self.get_username()
		await self.send_connect()

	def initialize_game_state(self):
		"""Initialize tracking dictionaries from game data."""
		self.game_memory.init_level_dat(self)

	async def game_watcher(self):
		while True:
			if not dme.is_hooked():
				raise ConnectionResetError(
					"Dolphin disconnected."
				)
			await self.check_levels()
			await asyncio.sleep(0.5)

	async def check_levels(self):
		gameState = self.memory_editor.getLevelStatesFromGame()
		previousState = self.game_memory.level_state




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
			if (not self.ranksanity): # {
				# Don't bother making this if ranksanity is enabled, bugs show up nicer if it crashes :)
				self.requiredRank = args["slot_data"]["Required Rank"]
			self.useEndless = args["slot_data"]["Include Endless"]
			self.remixCount = args["slot_data"]["Remix Count"]


		elif cmd == "ReceivedItems":
			for item in args["items"]:
				asyncio.create_task(
					self.handle_received_item(item)
				)

		super().on_package(cmd, args)

	async def handle_received_item(self, item):
		"""Translate AP items into game-memory changes."""
		if self.game_memory is None:
			return
		# }
		if (item[0:5] == "Album"): # {
			# We can assume that we aren't using levelsanity as the Album item should not be made with it on
			self.memory_editor.unlockAlbum(item[-2:].strip())
		levels = []
		for remix in worlds.rhythm_heaven_fever.levels_dict["core"]:
			levels.extend(worlds.rhythm_heaven_fever.levels_dict["core"][remix])
		elif item ==

	# Location detection methods go here.
	# Item application methods go here.