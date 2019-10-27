from .vector import Vector

OSU_OBJ_CIRCLE:int = 1<<0
OSU_OBJ_SLIDER:int = 1<<1
OSU_OBJ_SPINNER:int = 1<<3

class OsuHitObject(object):
	"""
		repetitions a general hit objects, no matter what type
		it should be used as a parent class, since there are values every object has
	"""
	def __init__(self, starttime:float or str):
		self.osu_obj:int = 0
		self.starttime:float = float(starttime)
		self.Pos:Vector = Vector()
		self.NormPos:Vector = Vector()
		self.angle:float = 0.0
		self.strains:list = [0.0, 0.0]
		self.is_single:bool = False
		self.delta_time:float = 0.0
		self.delta_distance:float = 0.0

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return f"<{self.__class__.__name__} {self.starttime}ms Pos={self.Pos} NormPos={self.NormPos} strains={self.strains} is_single={str(self.is_single)}>"

class OsuHitObjectCircle(OsuHitObject):
	"""
		representats a single circle object
	"""
	def __init__(self, starttime:float or str, Pos:Vector=None):
		super().__init__(starttime)
		if not Pos: Pos = Vector()

		self.osu_obj = OSU_OBJ_CIRCLE
		self.Pos = Pos

class OsuHitObjectSlider(OsuHitObject):
	"""
		representats a single slider object
	"""
	def __init__(self, starttime:float or str, Pos:Vector=None, distance:float or str=0.0, repetitions:int or str=0):
		super().__init__(starttime)
		if not Pos: Pos = Vector()

		self.osu_obj = OSU_OBJ_SLIDER
		self.Pos = Pos
		self.distance:float = float(distance)
		self.repetitions:int = int(repetitions)

class OsuHitObjectSpinner(OsuHitObject):
	"""
		a spinner, yeahhhh...
	"""
	def __init__(self, starttime:float, endtime:float or str=0.0):
		super().__init__(starttime)

		self.osu_obj = OSU_OBJ_SPINNER
		self.endtime:float = float(endtime)
