from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

DIFF_SPEED:int = 0
DIFF_AIM:int = 1

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

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} total={round(self.total, 2)} (aim={round(self.aim, 2)} speed={round(self.speed, 2)})>"

	def __str__(self) -> str:
		return self.__repr__()

	def calc(self) -> None:
		self.Map
