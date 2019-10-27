from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

import math
from .osumod import OsuModIndex
from .osustats import OsuStats
from .osudifficulty import OsuDifficulty
from .osugamemode import MODE_STD

class OsuPP(object):
	"""
		Holds all methods to get the wanted pp values
	"""
	def __init__(self, Map:"OsuMap"):
		self.Map:"OsuMap" = Map

	def calc(self, version:int=2, accuracy:float=100, combo:int=None, misses:int=0, n300:int=None, n100:int=None, n50:int=None) -> None:
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
			combo = max_combo

		Stats:OsuStats = self.Map.getStats()
		Difficulty:OsuDifficulty = self.Map.getDifficulty()

		if self.Map.mode != MODE_STD and version == 2:
			raise NotImplementedError("no need to ppV2")

		# re-calc accuracy
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
			pass

		else:
			raise NotImplementedError(f"unknown score version: {version}")

		# global vars
		amount_hitobjects:int = len(self.Map.hitobjects)
		amount_objects_ober_2k:float = amount_hitobjects
		length_bonus:float = 0.95 + (0.4 * min(1, amount_objects_ober_2k))

		if amount_hitobjects > 2000:
			length_bonus += math.log10(amount_hitobjects) * 0.5

		miss_penality:float = 0.97 ** misses
		combo_break:float = (combo**0.8) / (max_combo**0.8)


		# ar bonus
		ar_bonus:float = 1.0
		if Difficulty.ar > 10.33:
			ar_bonus += 0.3 * (Difficulty.ar - 10.33)

		elif Difficulty.ar < 8.0:
			ar_bonus += 0.1 * (8.0 - Difficulty.ar)

		# aim pp
		aim_pp:float = self.getBasePP(Stats.aim)
		aim_pp *= length_bonus
		aim_pp *= miss_penality
		aim_pp *= combo_break
		aim_pp *= ar_bonus

		# hd bonus
		if Difficulty.mods_value & OsuModIndex.getValueFromString("HD"):
			aim_pp *= (1 + ( 0.04 * (12 - Difficulty.ar) ))

		# fl bonus
		if Difficulty.mods_value & OsuModIndex.getValueFromString("FL"):
			fl_bonus:float = 1 + (0.35 * min(1, amount_hitobjects/200))

			if amount_hitobjects > 200:
				fl_bonus += 0.3 * min(1, ((amount_hitobjects-200)/300) )

			if amount_hitobjects > 500:
				fl_bonus += (amount_hitobjects-500) / 1200  

			aim_pp *= fl_bonus

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
