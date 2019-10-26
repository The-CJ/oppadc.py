class GeneralOsuMod(object):
	"""
		represents a mod in osu
		value should be a one bit moved value (8,32,128,4096)
	"""
	def __init__(self, value:int, name:str=None, build:bool=False):
		self.value:int = value
		self.name:str = name or "[N/A]"
		self.build:bool = build

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} name='{self.name}' ({self.value})>"

	def __str__(self) -> str:
		return self.__repr__()

class OsuModIndex(object):
	"""
		Holds all ingame mods and provides some utils
	"""
	def __init__(self):
		self.mods_keys:list = ["KEY1", "KEY2", "KEY3", "KEY4", "KEY5", "KEY6", "KEY7", "KEY8", "KEY9", "KEYCO"]
		self.mods_free:list = ["NF", "EZ", "HD", "HR", "SD", "FL", "FI", "RX", "RX2", "SO", "KeyMods"]
		self.mods_score:list = ["HD", "HR", "DT", "FL", "FI"]
		self.index:dict = dict(
			NM = GeneralOsuMod(0, "No Mod"),
			NF = GeneralOsuMod(1, "No fail"),
			EZ = GeneralOsuMod(1<<1, "Easy"),
			TD = GeneralOsuMod(1<<2, "TouchDevice"),
			HD = GeneralOsuMod(1<<3, "Hidden"),
			HR = GeneralOsuMod(1<<4, "Hardrock"),
			SD = GeneralOsuMod(1<<5, "Sudden death"),
			DT = GeneralOsuMod(1<<6, "Double time"),
			RX = GeneralOsuMod(1<<7, "Relax"),
			HT = GeneralOsuMod(1<<8, "Half time"),
			NC = GeneralOsuMod(1<<9, "Nightcore"),
			FL = GeneralOsuMod(1<<10, "Flashlight"),
			AP = GeneralOsuMod(1<<11, "Autoplay"),
			SO = GeneralOsuMod(1<<12, "Spun out"),
			RX2 = GeneralOsuMod(1<<13, "Autopilot"),
			PF = GeneralOsuMod(1<<14, "Perfect"),
			KEY4 = GeneralOsuMod(1<<15, "4 Keys"),
			KEY5 = GeneralOsuMod(1<<16, "5 Keys"),
			KEY6 = GeneralOsuMod(1<<17, "6 Keys"),
			KEY7 = GeneralOsuMod(1<<18, "7 Keys"),
			KEY8 = GeneralOsuMod(1<<19, "8 Keys"),
			FI = GeneralOsuMod(1<<20, "Fade In"),
			RA = GeneralOsuMod(1<<21, "Random"),
			CI = GeneralOsuMod(1<<22, "Cinema"),
			TP = GeneralOsuMod(1<<23, "Target practice"),
			KEY9 = GeneralOsuMod(1<<24, "9 Keys"),
			KEYCO = GeneralOsuMod(1<<25, "Coop Keys"),
			KEY1 = GeneralOsuMod(1<<26, "1 Key"),
			KEY3 = GeneralOsuMod(1<<27, "2 Keys"),
			KEY2 = GeneralOsuMod(1<<28, "3 Keys"),
			SV2 = GeneralOsuMod(1<<29, "Score V2"),
			MI = GeneralOsuMod(1<<30, "Mirror")
		)

		self.index["KeyMods"] = self.buildMod(from_mods=self.mods_keys, name="Any Keys")
		self.index["FreeMods"] = self.buildMod(from_mods=self.mods_free, name="Allowed in multiplier")
		self.index["ScoreMods"] = self.buildMod(from_mods=self.mods_score, name="Increase Score")

	def get(self, name:str, alt=None) -> GeneralOsuMod:
		return self.index.get(name, alt)

	def getValueFromString(self, mod_str:str) -> int:
		"""
			returns the value of the string representation of mod groups

			HDHRFL -> 1048 (10000011000)

			does only work for 2 char mods
			else use getValueFromList
		"""
		res:int = 0
		while mod_str:
			search:str = mod_str[:2]

			FoundMod:GeneralOsuMod = self.get(search)
			if FoundMod:
				res |= FoundMod.value

			mod_str = mod_str[2:]

		return res

	def getValueFromList(self, mod_list:list) -> int:
		"""
			returns the value of all found mods

			['EZ','DT','KEY4'] -> 32834 (1000000001000100)
		"""
		res:int = 0
		for search in mod_list:

			FoundMod:GeneralOsuMod = self.get(search)
			if FoundMod:
				res |= FoundMod.value

		return res

	def getStringFromValue(self, value:int) -> str:
		"""
			returns the user known string representation for a mod value

			16648 -> HDHTPF
		"""

		if not value: return "NM"

		res:str = ""
		for mod in self.index:
			Mod:GeneralOsuMod = self.index[mod]
			if value & Mod.value and not Mod.build:
				res += mod

		return res

	def buildMod(self, value:int=None, from_mods:list=[], name:str=None) -> GeneralOsuMod:
		"""
			Builds a new mod,
			give it a name and a value,
			or a list of mod indexes to generate the value from it

			you can use this to generate 'presets'
			e.g.:
				Tryhard = OsuModIndex.buildMod(name="Tryhard mode", from_mods=["HD","HR"])
				So you can later Calculate a map and just give this object
		"""
		if value != None:
			return GeneralOsuMod(value, name, build=True)

		i:int = 0
		for m in from_mods:
			i |= self.get(m).value

		return GeneralOsuMod(i, name, build=True)

OsuModIndex:OsuModIndex = OsuModIndex()
