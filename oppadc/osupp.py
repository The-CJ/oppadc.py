from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

import math
from .osumod import OsuModIndex
from .osustats import OsuStats
from .osudifficulty import OsuDifficulty
from .osugamemode import MODE_STD

MOD_HD:int = OsuModIndex.getValueFromString("HD")
MOD_FL:int = OsuModIndex.getValueFromString("FL")
MOD_SO:int = OsuModIndex.getValueFromString("FL")
MOD_NF:int = OsuModIndex.getValueFromString("FL")

class OsuPP(object):
	"""
		Holds all methods to get the wanted pp values
	"""
	def __init__(self, Map:"OsuMap"):
		self.Map:"OsuMap" = Map

		self.accuracy:float = 0.0
		self.combo:int = 0
		self.misses:int = 0

		self.total_pp:float = 0.0
		self.aim_pp:float = 0.0
		self.speed_pp:float = 0.0
		self.acc_pp:float = 0.0

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return f"<{self.__class__.__name__} total={round(self.total_pp,3)}pp (aim={round(self.aim_pp,2)} speed={round(self.speed_pp,2)} acc={round(self.acc_pp,2)}) [{round(self.accuracy,2)}%]>"

	def calc(self, version:int=1, accuracy:float=100, combo:int=None, misses:int=0, n300:int=None, n100:int=None, n50:int=None) -> None:
		"""
			calculates the total pp (by standard PPv2) with the called arguments
			if its not given its always assumed to be the highest/best.
			also, only give 1: accuracy or (n300, n100, n50)
			not both, prefered are (n300, n100, n50), since there are the total known values
			but it can be calculated back to these from value

			If you provide both, (n300, n100, n50) are taken
		"""

		# we don't got all values from the user, so let calculate back from acc
		if not (n300 != None and n100 != None and n50 != None):
			n300, n100, n50 = self.getValuesFromAcc(accuracy, misses)

		# got no combo values, so we assume max combo
		max_combo:int = self.Map.maxCombo()
		if not combo or combo < 0:
			combo = max_combo - misses

		Stats:OsuStats = self.Map.getStats()
		Difficulty:OsuDifficulty = self.Map.getDifficulty()

		if self.Map.mode != MODE_STD and version == 2:
			raise NotImplementedError("no need to ppV2")

		# re-calc accuracy
		amount_hitobjects:int = len(self.Map.hitobjects)
		amount_circle:int = self.Map.amount_circle

		accuracy = self.getAccFromValues(n300, n100, n50, misses)
		real_acc:float = accuracy

		if version == 1:
			# scorev1 ignores sliders since they are free 300s,
			# for whatever reason it also ignores spinners
			real_acc = self.getAccFromValues(
				(n300 - self.Map.amount_slider - self.Map.amount_spinner),
				n100,
				n50,
				misses
			)

			# can go negative if we miss everything
			real_acc = max(0.0, real_acc)

		elif version == 2:
			amount_circle = amount_hitobjects

		else:
			raise NotImplementedError(f"unknown score version: {version}")

		# global vars
		amount_hitobjects:int = len(self.Map.hitobjects)
		amount_objects_ober_2k:float = amount_hitobjects / 2000
		length_bonus:float = 0.95 + (0.4 * min(1, amount_objects_ober_2k))

		if amount_hitobjects > 2000:
			length_bonus += math.log10(amount_objects_ober_2k) * 0.5

		miss_penality_aim:float = 0.97 * pow(1 - pow(misses / amount_hitobjects, 0.775), misses)
		miss_penality_speed:float = 0.97 * pow(1 - pow(misses / amount_hitobjects, 0.775), pow(misses, 0.875))
		combo_break:float = (combo**0.8) / (max_combo**0.8)

		# ar bonus
		ar_bonus:float = 0.0
		if Difficulty.ar > 10.33:
			ar_bonus += 0.4 * (Difficulty.ar - 10.33)

		elif Difficulty.ar < 8.0:
			ar_bonus += 0.1 * (8.0 - Difficulty.ar)

		# aim pp - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		self.aim_pp = self.getBasePP(Stats.aim)
		self.aim_pp *= length_bonus
		if misses > 0:
			self.aim_pp *= miss_penality_aim
		self.aim_pp *= combo_break
		self.aim_pp *= (1 + min(ar_bonus, ar_bonus * (amount_hitobjects / 1000)))

		# hd bonus
		hd_bonus:float = 1.0
		if Difficulty.mods_value & MOD_HD:
			hd_bonus += (0.04 * (12 - Difficulty.ar))
			self.aim_pp *= hd_bonus

		# fl bonus
		if Difficulty.mods_value & MOD_FL:
			fl_bonus:float = 1 + (0.35 * min(1, amount_hitobjects/200))

			if amount_hitobjects > 200:
				fl_bonus += 0.3 * min(1, ((amount_hitobjects-200)/300) )

			if amount_hitobjects > 500:
				fl_bonus += (amount_hitobjects-500) / 1200

			self.aim_pp *= fl_bonus

		# acc and od bonus
		acc_bonus:float = 0.5 + (accuracy / 2)
		od_squared = Difficulty.od * Difficulty.od
		od_bonus:float = 0.98 + (od_squared / 2500)

		self.aim_pp *= acc_bonus
		self.aim_pp *= od_bonus

		# speed pp - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		self.speed_pp = self.getBasePP(Stats.speed)
		self.speed_pp *= length_bonus
		if misses > 0:
			self.speed_pp *= miss_penality_speed
		self.speed_pp *= combo_break

		# high ar bonus
		if Difficulty.ar > 10.33:
			self.speed_pp *= 1 + min(ar_bonus, ar_bonus * (amount_hitobjects / 1000))

		# hd bonus
		self.speed_pp *= hd_bonus

		# more stuff added
		self.speed_pp *= (0.95 + od_squared / 750)
		self.speed_pp *= accuracy ** ((14.5 - max(Difficulty.od, 8)) / 2)
		if n50 >= amount_hitobjects / 500:
			self.speed_pp *= 0.98 ** (n50 - amount_hitobjects / 500)

		# acc pp - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		self.acc_pp = (1.52163 ** Difficulty.od) * (real_acc ** 24) * 2.83

		# length bonus (not the same as speed/aim length bonus)
		self.acc_pp *= min(1.15, ((amount_circle/1000) ** 0.3))

		if Difficulty.mods_value & MOD_HD:
			self.acc_pp *= 1.08

		if Difficulty.mods_value & MOD_FL:
			self.acc_pp *= 1.02

		# total pp - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
		final_multiplier:float = 1.12

		if Difficulty.mods_value & MOD_NF:
			final_multiplier *= max(0.9, 1 - 0.2 * misses)

		if Difficulty.mods_value & MOD_SO:
			final_multiplier *= 1 - (self.Map.amount_spinner / amount_hitobjects) ** 0.85

		self.total_pp = (( (self.aim_pp**1.1) + (self.speed_pp**1.1) + (self.acc_pp**1.1) ) ** (1.0/1.1)) * final_multiplier
		# set the vars we calculated with
		self.accuracy = accuracy * 100
		self.combo = combo
		self.misses = misses

	def getBasePP(self, stars:float) -> float:
		return (((5 * max( 1, (stars / 0.0675) )) - 4) ** 3) / 100000

	def getValuesFromAcc(self, accuracy:float, misses:float) -> tuple:
		"""
			tryed to get to the closest amount of n300, n100, n50
			based of the accuracy and misses
		"""

		amount_hitobjects:int = len(self.Map.hitobjects)

		misses = min(amount_hitobjects, misses)
		max_n300:float = amount_hitobjects - misses
		max_acc:float = self.getAccFromValues(max_n300, 0, 0, misses) * 100
		accuracy = max(0.0, min(max_acc, accuracy))

		n50:int = 0
		n300:int = 0

		# NOTE from Francesco149:
		# just some black magic maths from wolfram alpha
		n100:int = int(round( -3.0 * ((((accuracy * 0.01) - 1.0) * amount_hitobjects) + misses) * 0.5 ))

		if n100 > (amount_hitobjects - misses):
			# acc lower than all 100s, use 50s
			n100 = 0
			n50 = int(round( -6.0 * ((((accuracy * 0.01) - 1.0) * amount_hitobjects) + misses) * 0.5 ))
			n50 = min(max_n300, n50)

		else:
			n100 = min(max_n300, n100)

		n300 = amount_hitobjects - n100 - n50 - misses

		return (n300, n100, n50)

	def getAccFromValues(self, n300:int, n100:int, n50:int, misses:int) -> float:
		"""
			calculate accuracy (0.0 - 1.0)
		"""

		total:int = n300 + n100 + n50 + misses
		if total <= 0: return 0.0

		return ((n50 * 50) + (n100 * 100) + (n300 * 300)) / (total * 300)
