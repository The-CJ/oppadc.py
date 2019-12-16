from typing import Generator, Iterator

import math
from .osumod import GeneralOsuMod
from .osustats import OsuStats
from .osudifficulty import OsuDifficulty
from .osupp import OsuPP
from .osutimingpoint import OsuTimingPoint
from .osuobject import (
	OSU_OBJ_CIRCLE, OSU_OBJ_SLIDER, OSU_OBJ_SPINNER,
	OsuHitObjectCircle, OsuHitObjectSlider, OsuHitObjectSpinner
)
from .osugamemode import MODE_STD

class OsuMap(object):
	"""
		contains all meta data about a map
		holds the calculated results for pp in self.Calc
		and difficulty with applied mods n self.Diff (self.ar, cs, etc... contains the unmodified version)
	"""
	def __init__(self, file_path:str=None, raw_str:str=None, auto_parse:bool=True):
		self.__Diff:OsuDifficulty = None
		self.__Stat:OsuStats = None
		self.__PP:OsuPP = None

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
		return f"<{self.__class__.__name__} title='{self.title}' set={self.mapset_id} map={self.map_id}>"

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
		print_info.append( f"Slider - mult:x{self.slider_multiplier} tickrate:{self.slider_tick_rate}" )

		# objects
		print_info.append( f"Objects - Circle:x{self.amount_circle} Splider:x{self.amount_slider} Spinner:x{self.amount_spinner}" )

		# combo
		print_info.append( f"Max combo: x{self.maxCombo()}" )

		# hit objects list
		print_info.append( f"Hit Object List:" )
		if self.hitobjects:
			for Ob in self.hitobjects: print_info.append( (" " * 4) + str(Ob) )
		else:
			print_info.append( (" "*4) + "None" )

		# timing point list
		print_info.append( f"Timing Point List:" )
		if self.timingpoints:
			for Ob in self.timingpoints: print_info.append( (" " * 4) + str(Ob) )
		else:
			print_info.append( (" "*4) + "None" )

		return "\n".join(print_info)

	# parse utils
	def lineGenerator(self) -> Generator[str, None, None]:
		if not self.raw_str and not self.file_path:
			raise AttributeError("missing raw content or path to file")

		elif self.raw_str:
			for line in self.raw_str.splitlines():
				yield line

		elif self.file_path:
			FileObject:Iterator[str] = open(self.file_path, mode='r', encoding="UTF-8")
			self.found = True
			for line in FileObject:
				yield line

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

		Source:Generator[str, None, None] = self.lineGenerator()

		section:str = ""

		for line in Source:
			# ignore all types of commants
			if not line: continue
			if line[0] in [" ", "_"]: continue
			if line[0:2] == "//": continue

			line = line.strip()
			if not line: continue

			# change current section
			if line.startswith("["):
				section = line[1:-1]
				continue

			try:
				if not section:
					format_str:str = "file format v"
					findatpos:int = line.find(format_str)
					if findatpos > 0:
						self.format_version = int( line[findatpos+len(format_str):] )

				elif section == "General":
					self.parseGeneral(line)
				elif section == "Metadata":
					self.parseMetadata(line)
				elif section == "Difficulty":
					self.parseDifficulty(line)
				elif section == "TimingPoints":
					self.parseTimingPoint(line)
				elif section == "HitObjects":
					self.parseHitObject(line)

			except (ValueError, SyntaxError) as e:
				raise e

		# i did not know that this is a thing
		if not self.ar:
			self.ar = self.od

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

	def parseDifficulty(self, line:str) -> None:
		prop:tuple = self.parseProp(line)

		if prop[0] == "CircleSize":
			self.cs = float(prop[1])
		elif prop[0] == "OverallDifficulty":
			self.od = float(prop[1])
		elif prop[0] == "ApproachRate":
			self.ar = float(prop[1])
		elif prop[0] == "HPDrainRate":
			self.hp = float(prop[1])
		elif prop[0] == "SliderMultiplier":
			self.slider_multiplier = float(prop[1])
		elif prop[0] == "SliderTickRate":
			self.slider_tick_rate = float(prop[1])

	# timing
	def parseTimingPoint(self, line:str) -> None:
		# starttime, mspb, ?, ?, ?, ?, change, ?
		# each timing points can contains up to 8 ',' separated values
		s:list = line.split(',')

		if len(s) > 8:
			print("timing point with trailing values")

		elif len(s) < 2:
			raise SyntaxError("timing point must have at least two fields")

		TPoint:OsuTimingPoint = OsuTimingPoint( starttime=s[0], ms_per_beat=s[1] )
		if len(s) >= 7:
			TPoint.change = bool(s[6] != "0")

		self.timingpoints.append(TPoint)

	# hit objects
	def parseHitObject(self, line:str) -> None:
		if self.mode == MODE_STD:
			self.parseHitObjectSTD(line)

		else:
			raise NotImplementedError()

	def parseHitObjectSTD(self, line:str) -> None:
		# each hitobject can contains up to 11 ',' separated values
		s:list = line.split(',')

		if len(s) > 11:
			print("hit object with trailing values")

		elif len(s) < 5:
			raise SyntaxError("hitobject must have at least 5 fields")

		starttime:float = float(s[2])
		objtype:int = int(s[3])

		if not (0 <= objtype <= 255):
			raise SyntaxError("invalid hitobject type")

		# circle
		# x, y, starttime, objtype, ?, ?, ?, ?, ?, ?, ?
		if objtype & OSU_OBJ_CIRCLE:
			Circle:OsuHitObjectCircle = OsuHitObjectCircle(starttime)
			Circle.Pos.x = float(s[0])
			Circle.Pos.y = float(s[1])
			self.amount_circle += 1
			self.hitobjects.append(Circle)

		# ?, ?, starttime, objtype, ?, endtime, ?, ?, ?, ?, ?
		elif objtype & OSU_OBJ_SPINNER:
			Spinner:OsuHitObjectSpinner = OsuHitObjectSpinner(starttime)
			Spinner.endtime = float(s[5])
			self.amount_spinner += 1
			self.hitobjects.append(Spinner)

		# x, y, starttime, objtype, ?, repetitions, distance, ?, ?, ?, ?
		elif objtype & OSU_OBJ_SLIDER:
			if len(s) < 7:
				raise SyntaxError("slider must have at least 7 fields")

			Slider:OsuHitObjectSlider = OsuHitObjectSlider(starttime, repetitions=s[6], distance=s[7])
			Slider.Pos.x = float(s[0])
			Slider.Pos.y = float(s[1])

			self.amount_slider += 1
			self.hitobjects.append(Slider)

	# calculations
	def maxCombo(self) -> int:
		res:int = 0

		timing_index:int = -1
		CurrentTimingPoint:OsuTimingPoint = None
		NextTimingPoint:OsuTimingPoint = OsuTimingPoint(starttime=0)

		px_per_beat:float = 1.0

		# everything that not a slider is worth +1
		# sliders are another number duh
		for Obj in self.hitobjects:
			if not Obj.osu_obj & OSU_OBJ_SLIDER:
				res += 1
				continue

			# slider combo calc, for that we need data from the object itself,
			# as well data of the currently active timing point.

			# when our object has a higher starttime that our next timing point,
			# and we still have a next timingpoint
			# then CurrentTimingPoint = NextTimingPoint
			# and we try to get a next one, or set None to ignore loop
			while NextTimingPoint is not None and Obj.starttime >= NextTimingPoint.starttime:
				timing_index += 1
				CurrentTimingPoint = self.timingpoints[timing_index]

				# is there a next?
				if len(self.timingpoints) > (timing_index + 1):
					NextTimingPoint = self.timingpoints[timing_index + 1]
				else:
					NextTimingPoint = None

				slider_speed_multiplier:float = 1.0

				if not CurrentTimingPoint.change and CurrentTimingPoint.ms_per_beat < 0:
					slider_speed_multiplier = (-100 / CurrentTimingPoint.ms_per_beat)

				px_per_beat = self.slider_multiplier * 100 * slider_speed_multiplier
				if self.format_version < 8:
					px_per_beat /= slider_speed_multiplier

			# get the number of beat
			beats:float = (Obj.distance * Obj.repetitions) / px_per_beat
			# get the slider ticks, this is what actully increases the combo
			ticks:int = math.ceil( (beats - 0.1) / Obj.repetitions * self.slider_tick_rate )

			# remove endpoint from ticks
			ticks -= 1
			# times the repetition
			ticks *= Obj.repetitions
			# add one more repetition and re-add endpoint
			ticks += Obj.repetitions + 1

			# we do this because...
			# well i really don't know, can there be negative values?
			# @Francesco149 probly has a reason for this
			res += max(0, ticks)

		return res

	def getDifficulty(self, Mods:GeneralOsuMod or list or str=None, recalculate:bool=False) -> OsuDifficulty:
		if self.__Diff and not recalculate: return self.__Diff

		self.__Diff = OsuDifficulty(self)
		self.__Diff.applyMods(Mods)
		return self.__Diff

	def getStats(self, Mods:GeneralOsuMod or list or str=None, recalculate:bool=False) -> OsuStats:
		if self.__Stat and not recalculate: return self.__Stat

		# generate diff object, its needed during the calc process
		self.getDifficulty(Mods=Mods, recalculate=recalculate)

		self.__Stat = OsuStats(self)
		self.__Stat.calc()
		return self.__Stat

	def getPP(self, Mods:GeneralOsuMod or list or str=None, recalculate:bool=False, **kwargs:dict) -> OsuPP:
		"""
			allowed kwargs:
				accuracy:float
				combo:int
				misses:int
				n300:int
				n100:int
				n50:int
		"""
		if self.__PP and not recalculate: return self.__PP

		# to calculate the pp, we need the stats, which needs the applied difficulty
		# aka, u want pp, u calculate everything
		self.getStats(Mods=Mods, recalculate=recalculate)

		self.__PP = OsuPP(self)
		self.__PP.calc(**kwargs)
		return self.__PP
