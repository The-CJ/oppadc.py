from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

class OsuPP(object):
	"""
		Holds all methods to get the wanted pp values
	"""
	def __init__(self, Map:"OsuMap"):
		self.Map:"OsuMap" = Map

	def calc(self) -> None:
		pass
