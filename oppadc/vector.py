import math

class Vector:
	"""
		A 2D vector
	"""
	def __init__(self, x:float=0.0, y:float=0.0):
		self.x:float = x
		self.y:float = y

	def __sub__(self, Other:"Vector") -> "Vector":
		return Vector(self.x-Other.x, self.y-Other.y)

	def __mul__(self, factor:float) -> "Vector":
		return Vector(self.x*factor, self.y*factor)

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} x={self.x} y={self.y}>"

	def __str__(self) -> str:
		return self.__repr__()

	def dot(self, Other:"Vector") -> float:
		return (self.x*Other.x) + (self.y*Other.y)

	@property
	def length(self) -> float:
		return math.sqrt( (self.x**2) + (self.y**2) )
