import jinja2

from ..data import levels_dict

class Address: # {
	slot_starts = [
		0x906692FC,
		0x9066957C,
		0x906697FC,
		0x90669A7C
	]

	def __init__(self, slotNum=-1):
		self.slot = slotNum
		self.levels = []

		for remix in levels_dict["core"]: # {
			for level in levels_dict["core"][remix]: # {
				self.levels.append(level)
			# }
			self.levels.append(remix)

		startAddr = self.slot_starts[self.slot]



		self.colCountAddr = startAddr + 0x09
		self.lastPlayedLevelAddr = startAddr + 0x0a

		self.levelStatusDictToAddri = {
			levelName: startAddr + i
			for levelName, i in zip(self.levels, range(0x0b, 0x3c))
		}

		self.loadLeftmostColAddr = startAddr + 0x3d
		self.levelPointsAddri = [startAddr + i for i in range(0x3e, 0xa1)]

		self.gameRecalculateTellerAddr = startAddr + 0xa2
		self.mayBeStatusOfPreviousLevelAddr = startAddr + 0xa3
		self.pointsMultAddr = startAddr + 0xa4

		self.wakeupCallerPointsAddr = startAddr + 0xec
		self.muchMonkPointsAddr = startAddr + 0xf0
		self.ladyCupidPointsAddr = startAddr + 0xf4
		self.mrUpbeatPointsAddr = startAddr + 0xf8
		self.endlessRemixPointsAddr = startAddr + 0xfc

		self.profileTypeAddr = startAddr + 0x250
		self.firstTimeInCafeAddr = startAddr + 0x251
		self.baristaCongratulatesPerfectCampaignDoneAddr = startAddr + 0x252
		self.firstTimeInDualPlayAddr = startAddr + 0x253
		self.englishOrSpanishVoiceAddr = startAddr + 0x254

	def set_slot(self, slotNum):
		self.__init__(slotNum)