class GeneralOsuMod(object):
	"""
		represents a mod in osu
		value should be a one bit moved value (8,32,128,4096)
	"""
	def __init__(self, value:int, name:str=None):
		self.value:int = value
		self.name:str = name or "[N/A]"

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} name='{self.name}' ({self.value})>"

	def __str__(self) -> str:
		return self.__repr__()

index:dict = dict(
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



)
