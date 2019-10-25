from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

class OsuCalculator(object):
	"""
		contains everything to calculate pp
	"""
	def __init__(self, Map:"OsuMap"):
		self.Map:"OsuMap" = Map

		self.strains:list = []
		self.total:float = 0.0
		self.aim:float = 0.0
		self.aim_difficulty:float = 0.0
		self.aim_length_bonus:float = 0.0
		self.speed:float = 0.0
		self.speed_difficulty:float = 0.0
		self.speed_length_bonus:float = 0.0
		self.amount_singles:int = 0
		self.amount_singles_threshold:int = 0

	def calc() -> None:
		self.Map
