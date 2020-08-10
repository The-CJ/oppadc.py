from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

import math
from .osumod import GeneralOsuMod, OsuModIndex

MODS_SPEED_FASTER:int = OsuModIndex.getValueFromString("NCDT")
MODS_SPEED_SLOWER:int = OsuModIndex.getValueFromString("HT")

class OsuDifficulty(object):
	"""
		Contains the difficulty and allowes to apply mods.
		applying mods will change the stats
	"""
	def __init__(self, Map:"OsuMap"):
		self.Map:"OsuMap" = Map

		self.mods_str:str = ""
		self.mods_value:int = 0

		self.speed_multiplier:float = 1.0
		self.ar:float = Map.ar
		self.cs:float = Map.cs
		self.od:float = Map.od
		self.hp:float = Map.hp

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} ar={round(self.ar, 2)} cs={round(self.cs, 2)} od={round(self.od, 2)} hp={round(self.hp, 2)} mods='{self.mods_str}'>"

	def __str__(self) -> str:
		return self.__repr__()

	def applyMods(self, Mods:GeneralOsuMod or list or str or int=None, calc:list=["AR","OD","CS","HP"]) -> None:
		if not Mods: return

		mods_value:int = 0
		if type(Mods) is int:
			mods_value = Mods
		elif type(Mods) is str:
			mods_value = OsuModIndex.getValueFromString(Mods)
		elif type(Mods) is GeneralOsuMod:
			mods_value = Mods.value

		self.mods_value = mods_value
		self.mods_str = OsuModIndex.getStringFromValue(mods_value)

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

		OD_AR_HP_Multiplier:float = 1.0

		if mods_value & OsuModIndex.index["HR"].value:
			OD_AR_HP_Multiplier = 1.4

		elif mods_value & OsuModIndex.index["EZ"].value:
			OD_AR_HP_Multiplier = 0.5

		# AR
		if "AR" in calc:
			self.ar *= OD_AR_HP_Multiplier

			ar_ms:float = AR5_MS

			if self.ar < 5:
				ar_ms = AR0_MS - (AR_MS_STEP1 * self.ar)
			else:
				ar_ms = AR5_MS - (AR_MS_STEP2 * (self.ar - 5))

			# NOTE from Francesco149:
			# stats must be capped to 0-10 before HT/DT which brings
			# them to a range of -4.42-11.08 for OD and -5-11 for AR
			ar_ms = min(AR0_MS, max(AR10_MS, ar_ms))
			ar_ms /= self.speed_multiplier

			# convert back to AR
			if ar_ms > AR5_MS:
				self.ar = (AR0_MS - ar_ms) / AR_MS_STEP1
			else:
				self.ar = 5.0 + (AR5_MS - ar_ms) / AR_MS_STEP2

		if "OD" in calc:
			self.od *= OD_AR_HP_Multiplier

			od_ms:float = OD0_MS - math.ceil(OD_MS_STEP * self.od)
			od_ms = min(OD0_MS, max(OD10_MS, od_ms))
			od_ms /= self.speed_multiplier

			self.od = (OD0_MS - od_ms) / OD_MS_STEP

		if "CS" in calc:
			if mods_value & OsuModIndex.index["HR"].value:
				self.cs *= 1.3

			elif mods_value & OsuModIndex.index["EZ"].value:
				self.cs *= 0.5

			self.cs = min(10, self.cs)

		if "HP" in calc:
			self.hp = min(10, self.hp * OD_AR_HP_Multiplier)
