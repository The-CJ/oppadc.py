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
		print_info:str = []

		# artist
		if self.artist != self.artist_unicode:
			print_info.append( f"Artist: {self.artist_unicode} [{self.artist}]" )
		else:
			print_info.append( f"Artist: {self.artist}" )

		# title
		if self.title != self.title_unicode:
			print_info.append( f"Title: {self.title_unicode} [{self.title}]" )
		else:
			print_info.append( f"Title: {self.title}" )

		# creator
		print_info.append( f"Creator: {self.creator}" )

		# version
		print_info.append( f"Version: {self.version}" )

		# difficulty
		print_info.append( f"Difficulty - HP:{self.hp} CS:{self.cs} OD:{self.od} AR:{self.ar}" )

		# slider
		print_info.append( f"Slider - speed:{self.slider_multiplier} tickrate:{self.slider_tick_rate}" )

		# objects
		print_info.append( f"Objects - Circle:x{self.amount_circle} Splider:x{self.amount_slider} Spinner:x{self.amount_spinner}" )

		# hit objects list
		print_info.append( f"Hit Object List:" )

		# timing point list
		print_info.append( f"Timing Point List:" )

		return "\n".join(print_info)

	# parse utils
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

	def parseProp(self, line) -> tuple:
		"""
			get prop from line, also strip white spaces from value
		"""
		pair:list = line.split(':', 1)
		if len(pair) == 1:
			raise SyntaxError(f"property must me pair of ':'-separated values, can't get property from line: {line}")

		return (pair[0], pair[1].strip())

	def parse(self) -> None:

		Source:generator = self.lineGenerator()

		section:str = ""

		for line in Source:
			# ignore all types of commants
			if line[0] in [" ", "_"]: continue
			if line[0:2] == "//": continue

			line = line.strip()
			if not line: continue

			# change current section
			if line.startswith("["):
				section = line[1:-1]
				continue

			try:
				if section == "General":
					self.parseGeneral(line)
				elif section == "Metadata":
					self.parseMetadata(line)

			except (ValueError, SyntaxError) as e:
				raise e

		self.done = True

	def parseGeneral(self, line:str) -> None:
		prop:tuple = self.parseProp(line)

		if prop[0] == "Mode":
			self.mode = int(prop[1])

	def parseMetadata(self, line:str) -> None:
		prop:tuple = self.parseProp(line)

		if prop[0] == "Title":
			self.title = prop[1]
		elif prop[0] == "TitleUnicode":
			self.title_unicode = prop[1]
		elif prop[0] == "Artist":
			self.artist = prop[1]
		elif prop[0] == "ArtistUnicode":
			self.artist_unicode = prop[1]
		elif prop[0] == "Creator":
			self.creator = prop[1]
		elif prop[0] == "Version":
			self.version = prop[1]
		elif prop[0] == "Source":
			self.source = prop[1]
		elif prop[0] == "BeatmapID":
			self.map_id = int(prop[1])
		elif prop[0] == "BeatmapSetID":
			self.mapset_id = int(prop[1])
		elif prop[0] == "Tags":
			self.tags = [t.strip() for t in prop[1].split(',')]

	# calculations
