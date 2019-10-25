from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

from .osumod import GeneralOsuMod, OsuModIndex

MODS_SPEED_FASTER:int = OsuModIndex.getValueFromString("NCDT")
MODS_SPEED_SLOWER:int = OsuModIndex.getValueFromString("HT")

class OsuDifficulty(object):
	"""
		Contains the difficulty and allowes to apply mods.
		applying mods will change the stats
	"""
	def __init__(self, Map:"OsuMap"):
		self.speed_multiplier:float = 1.0
		self.ar:float = Map.ar
		self.cs:float = Map.cs
		self.od:float = Map.od
		self.hp:float = Map.hp

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} ar={round(self.ar, 2)} cs={round(self.cs, 2)} od={round(self.od, 2)} hp={round(self.hp ,2)}>"

	def __str__(self) -> str:
		return self.__repr__()

	def applyMods(self, Mods:GeneralOsuMod or list or str or int=None) -> None:
		if not Mods: return

		mods_value:int = 0
		if type(Mods) is int:
			mods_value = Mods
		elif type(Mods) is str:
			mods_value = OsuModIndex.getValueFromString(Mods)
		elif type(Mods) is GeneralOsuMod:
			mods_value = Mods.value

		OD0_MS:int = 80
		OD10_MS:int = 20
		AR0_MS:int = 1800
		AR5_MS:int = 1200
		AR10_MS:int = 450

		OD_MS_STEP:float = (OD0_MS - OD10_MS) / 10.0
		AR_MS_STEP1:float = (AR0_MS - AR5_MS) / 5.0
		AR_MS_STEP2:float = (AR5_MS - AR10_MS) / 5.0

		MODS_SPEED_CHANGING:int = OsuModIndex.getValueFromString("DTHTNC")
		MODS_MAP_CHANGING:int = MODS_SPEED_CHANGING | OsuModIndex.getValueFromString("HREZ")

		# no mods will change stuff we care about
		if not mods_value & MODS_MAP_CHANGING: return

		if mods_value & MODS_SPEED_FASTER:
			self.speed_multiplier = 1.5

		elif mods_value & MODS_SPEED_SLOWER:
			self.speed_multiplier = 0.75
