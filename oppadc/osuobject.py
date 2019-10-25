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
		self.starttime:float = float(starttime)
		self.NormPos:Vector = Vector()
		self.angle:float = 0.0
		self.strains:list = [0.0, 0.0]
		self.is_single:bool = False
		self.delta_time:float = 0.0
		self.delta_distance:float = 0.0

class OsuHitObjectCircle(OsuHitObject):
	"""
		representats a single circle object
	"""
	def __init__(self, starttime:float or str, Pos:Vector=Vector()):
		super().__init__(starttime)

		self.Pos:Vector = Pos

class OsuHitObjectSlider(OsuHitObject):
	"""
		representats a single slider object
	"""
	def __init__(self, starttime:float or str, Pos:Vector=Vector(), distance:float or str=0.0, repetitions:int or str=0):
		super().__init__(starttime)

		self.Pos:Vector = Pos
		self.distance:float = float(distance)
		self.repetitions:int = int(repetitions)
