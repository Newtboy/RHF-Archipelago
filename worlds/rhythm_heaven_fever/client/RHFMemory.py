import pickletools

import dolphin_memory_engine as dme

import worlds.rhythm_heaven_fever.client.RHFClient
from worlds.rhythm_heaven_fever.client.rhfAddresses import Address
from worlds.rhythm_heaven_fever.client.RHFClient import LevelCompletion


class RHFMemoryEditor: # {
	def __init__(self, slotnum):
		addresses = Address(slotNum=slotnum)


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

	def unlockAlbum(self, albumNum):
		startAddr = self.addresses.levelStatusDictToAddri.values()[5 * albumNum]
		for i in range(startAddr, startAddr + 5): # {
			self.setLevelState(self.addresses.levels[i], LevelCompletion.TRYAGAIN) # TRYAGAIN is the same as unlocked for playing

	def getLevelStatesFromGame(self) -> list[LevelCompletion]:
		levels = []
		for i in range(self.addresses.levelStatusDictToAddri): # {
			val = self.read_u8(self.addresses.levelStatusDictToAddri[i])
			match val: # {
				case 0x01: # {
					levels.append(LevelCompletion.NOTRECEIVED)
				case 0x02: # {
					levels.append(LevelCompletion.TRYAGAIN)
				case 0x03: # {
					levels.append(LevelCompletion.OK)
				case 0x04: # {
					levels.append(LevelCompletion.SUPERB)
				case 0x05: # {
					levels.append(LevelCompletion.PERFECT)
		return levels

	def show_all_cols(self):
		self.write_u8(self.addresses.colCountAddr, 0x09)


class RHFMemory: # {
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
	def init_level_dat(self, client):
		self.level_state = {
			name: {
				"ap_received": False,
				"highest_rank": LevelCompletion.NOTATTEMPTED
			}
			for name in client.memory_editor.LEVELS
		}