from typing import Generator, Iterator

class OsuMap(object):
	"""
		contains all meta data about a map
		also holds the calculated results for pp and diff
	"""
	def __init__(self, file_path:str=None, raw_str:str=None, auto_parse:bool=True):
		# internal
		self.file_path:str = file_path
		self.raw_str:str = raw_str
		self.found:bool = False
		self.done:bool = False

		# general
		self.mode:int = None
		self.format_version:int = 1

		# metadata
		self.title:str = ""
		self.title_unicode:str = ""
		self.artist:str = ""
		self.artist_unicode:str = ""
		self.creator:str = ""
		self.version:str = ""
		self.source:str = ""
		self.tags:list = []
		self.map_id:int = 0
		self.mapset_id:int = 0

		# difficulty
		self.hp:float = 5
		self.cs:float = 5
		self.od:float = 5
		self.ar:float = 5
		self.slider_multiplier:float = 1
		self.slider_tick_rate:float = 1

		# map objects
		self.amount_circle:int = 0
		self.amount_slider:int = 0
		self.amount_spinner:int = 0
		self.timingpoints:list = []
		self.hitobjects:list = []

		if auto_parse:
			self.parse()

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} title='{self.title}' set={self.mapset_id} map={self.map_id} >"

	def __str__(self) -> str:
		return self.__repr__()

	def lineGenerator(self) -> Generator[str, None, None]:
		if not self.raw_str and not self.file_path:
			raise AttributeError("missing raw content or path to file")

		elif self.raw_str:
			for line in self.raw_str.splitlines():
				yield line
			raise StopIteration()

		elif self.file_path:
			FileObject:Iterator[str] = open(self.file_path, mode='r', encoding="UTF-8")
			self.found = True
			for line in FileObject:
				yield line
			raise StopIteration()

		else:
			raise StopIteration()

	def parse(self) -> bool:

		Source:generator = self.lineGenerator()

		for line in Source:
			print(line)

		self.done = True
