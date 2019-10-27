from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

class OsuPP(object):
	"""
		Holds all methods to get the wanted pp values
	"""
	def __init__(self, Map:"OsuMap"):
		self.Map:"OsuMap" = Map

	def calc(self, accuracy:float=100, combo:int=None, misses:int=0, n300:int=None, n100:int=None, n50:int=None) -> None:
		"""
			calculates the total pp with the called arguments
			if its not given its always assumed to be the highest/best.
			also, only give 1: accuracy or (n300, n100, n50)
			not both, prefered are (n300, n100, n50), since there are the total known values
			but it can be calculated back to these from value

			If you provide both, (n300, n100, n50) are taken
		"""

		# we don't got all values from the user, so let calculate back from acc
		if not (n300 != None and n100 != None and n50 != None):
			n300, n100, n50 = self.valuesFromAcc(accuracy, misses)

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
