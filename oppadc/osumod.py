class GeneralOsuMod(object):
	"""
		represents a mod in osu
		value should be a one bit moved value (8,32,128,4096)
	"""
	def __init__(self, value:int, name:str=None):
		self.value:int = value
		self.name = name or "[N/A]"
