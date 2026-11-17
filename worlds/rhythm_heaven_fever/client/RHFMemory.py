import pickletools

import dolphin_memory_engine as dme

from worlds.rhythm_heaven_fever.client.rhfAddresses import Address
from worlds.rhythm_heaven_fever.client.RHFEnums import LevelCompletion

class RHFMemoryEditor: # {
	def __init__(self, slotnum):
		self.addresses = Address(slotNum=slotnum)
		self.last_status = {}


	def read_bytes(self, address, size):
		return dme.read_bytes(address, size)


	def write_bytes(self, address, data):
		dme.write_bytes(address, data)


	def read_u8(self, address):
		return int.from_bytes(
			self.read_bytes(address, 1),
			byteorder="big",
			signed=False
		)


	def write_u8(self, address, value):
		if not 0 <= value <= 0xFF:
			raise ValueError("u8 value out of range")

		self.write_bytes(
			address,
			value.to_bytes(1, byteorder="big", signed=False)
		)


	def read_u64(self, address):
		return int.from_bytes(
			self.read_bytes(address, 8),
			byteorder="big",
			signed=False
		)


	def write_u64(self, address, value):
		if not 0 <= value <= 0xFFFFFFFFFFFFFFFF:
			raise ValueError("u64 value out of range")

		self.write_bytes(
			address,
			value.to_bytes(8, byteorder="big", signed=False)
		)
	def setLevelState(self, level:str, completion: LevelCompletion):
		match completion: # {
			case LevelCompletion.NOTRECEIVED: # {
				val = 0x01
			case LevelCompletion.TRYAGAIN: # {
				val = 0x02
			case LevelCompletion.OK: # {
				val = 0x03
			case LevelCompletion.SUPERB: # {
				val = 0x04
			case LevelCompletion.PERFECT: # {
				val = 0x05
		self.write_u8(self.addresses.levelStatusDictToAddri[level], val)


	def unlockLevel(self, levelName):
		address = self.addresses.levelStatusDictToAddri[levelName]
		current_status = self.read_u8(address)

		# Unlock without overwriting existing completion ranks.
		if current_status in (0x00, 0x01):
			self.write_u8(address, 0x02)

	def lockLevel(self, levelName):
		address = self.addresses.levelStatusDictToAddri[levelName]
		current_status = self.read_u8(address)

		# Lock without overwriting existing completion ranks.
		if current_status in (0x00, 0x02):
			self.write_u8(address, 0x01)

	def unlockAlbum(self, albumNum):
		startIndex = 5 * (albumNum - 1)

		for level in self.addresses.levels[startIndex:startIndex + 5]:
			self.unlockLevel(level)

	def getLevelStatesFromGame(self) -> dict[str, LevelCompletion]:
		levels: dict[str, LevelCompletion] = {}

		for name, memAddr in self.addresses.levelStatusDictToAddri.items():
			val = self.read_u8(memAddr)

			# Print only when a memory value changes.
			if self.last_status.get(name) != val:
				print(
					f"[RHF Memory] {name}: "
					f"0x{memAddr:08X} = 0x{val:02X}"
				)
				self.last_status[name] = val

			match val:
				case 0x01:
					levels[name] = LevelCompletion.NOTRECEIVED
				case 0x02:
					levels[name] = LevelCompletion.TRYAGAIN
				case 0x03:
					levels[name] = LevelCompletion.OK
				case 0x04:
					levels[name] = LevelCompletion.SUPERB
				case 0x05:
					levels[name] = LevelCompletion.PERFECT
				case _:
					print(
						f"[RHF WARNING] Unknown status "
						f"0x{val:02X} for {name}"
					)

		return levels

	def show_all_cols(self):
		self.write_u8(self.addresses.colCountAddr, 0x09)


class RHFMemory: # {
	def __init__(self, client):
		self.level_state = {
			name: {
				"ap_received": False,
				"highest_rank": LevelCompletion.NOTRECEIVED
			}
			for name in self.LEVELS
		}

	LEVELS = [
		"Hole in One",
		"Screwbot Factory",
		"See-Saw",
		"Double Date",
		"Remix 1",
		"Fork Lifter",
		"Tambourine",
		"Board Meeting",
		"Monkey Watch",
		"Remix 2",
		"Working Dough",
		"Built to Scale",
		"Air Rally",
		"Figure Fighter",
		"Remix 3",
		"Ringside",
		"Packing Pests",
		"Micro-Row",
		"Samurai Slice",
		"Remix 4",
		"Catch of the Day",
		"Flipper-Flop",
		"Exhibition Match",
		"Flock Step",
		"Remix 5",
		"Launch Party",
		"Donk-Donk",
		"Bossa Nova",
		"Love Rap",
		"Remix 6",
		"Tap Troupe",
		"Shrimp Shuffle",
		"Cheer Readers",
		"Karate Man",
		"Remix 7",
		"Night Walk",
		"Samurai Slice 2",
		"Working Dough 2",
		"Built to Scale 2",
		"Double Date 2",
		"Remix 8",
		"Love Rap 2",
		"Cheer Readers 2",
		"Hole in One 2",
		"Screwbot Factory 2",
		"Remix 9",
		"Figure Fighter 2",
		"Micro-Row 2",
		"Packing Pests 2",
		"Karate Man 2",
		"Remix 10"
	]