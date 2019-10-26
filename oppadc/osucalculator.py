from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

import math
from .vector import Vector
from .osudifficulty import OsuDifficulty
from .osuobject import OsuHitObject, OSU_OBJ_SPINNER

DIFF_SPEED:int = 0
DIFF_AIM:int = 1

#strain stuff
DECAY_BASE:list = [ 0.3, 0.15 ] # strain decay per interval
WEIGHT_SCALING:list = [ 1400.0, 26.25 ] # balances speed and aim

class OsuCalculator(object):
	"""
		contains everything to calculate pp
	"""
	def __init__(self, Map:"OsuMap"):
		self.Map:"OsuMap" = Map

		self.strains:list = []
		self.total:float = 0.0
		self.aim:float = 0.0
		self.aim_difficulty:float = 0.0
		self.aim_length_bonus:float = 0.0
		self.speed:float = 0.0
		self.speed_difficulty:float = 0.0
		self.speed_length_bonus:float = 0.0
		self.amount_singles:int = 0
		self.amount_singles_threshold:int = 0

	def __repr__(self) -> str:
		return f"<{self.__class__.__name__} total={round(self.total, 2)}pp (aim={round(self.aim, 2)} speed={round(self.speed, 2)})>"

	def __str__(self) -> str:
		return self.__repr__()

	def calc(self) -> None:
		"""
			calculates everything and stores it in self.*
			self.total prob. is what most people want
			takes all changes made by mods in consideration.
			(
				aka it uses the Maps.__Diff,
				that is set by the maps.getCalc automaticly (or at least should)
			)

			NOTE: From Francesco149:
			singletap_threshold is the smallest milliseconds interval
			that will be considered singletappable, defaults to 125ms
			which is 240 bpm 1/2 ((60000 / 240) / 2)
		"""
		Difficulty:OsuDifficulty = self.Map.getDiff()

		# non-normalized diameter where the small circle size buff starts
		CIRCLESIZE_BUFF_THRESHOLD:int = 30
		STAR_SCALING_FACTOR:float = 0.0675 # global stars multiplier

		# 50% of the difference between aim and speed is added to
		# star rating to compensate aim only or speed only maps
		EXTREME_SCALING_FACTOR:float = 0.5
		PLAYFIELD_WIDTH:int = 512 # in osu!pixels
		PlayfieldCenter:Vector = Vector( PLAYFIELD_WIDTH / 2, PLAYFIELD_WIDTH / 2 )

		if self.Map.mode != 0:
			raise NotADirectoryError()

		circle_radius:float = ( (PLAYFIELD_WIDTH/16) * (1 - (0.7 * (Difficulty.cs - 5)) / 5) )

		# positions are normalized on circle radius,
		# so that we can calc as if everything was the same circlesize
		scaling_factor:float = 52.0 / circle_radius

		# low cs buff (credits to osuElements)
		if circle_radius < CIRCLESIZE_BUFF_THRESHOLD:
			scaling_factor *= (1.0 + min(CIRCLESIZE_BUFF_THRESHOLD - circle_radius, 5.0) / 50.0)

		# normalize playarea, based on circle size
		PlayfieldCenter *= scaling_factor

		# give every object a NormPos before calculating stuff
		self.calcNormPos(PlayfieldCenter, scaling_factor)

		# get pp and diff stats
		speed = self.calcIndividual(Difficulty, DIFF_SPEED)
		aim = self.calcIndividual(Difficulty, DIFF_AIM)

	def calcNormPos(self, PlayfieldCenter:Vector, scaling_factor:float) -> None:
		PrevObject1:OsuHitObject = None
		PrevObject2:OsuHitObject = None
		i:int = 0
		for Obj in self.Map.hitobjects:
			Obj:OsuHitObject = Obj

			# spinner dont have a position, so we give it one
			if Obj.osu_obj & OSU_OBJ_SPINNER:
				Obj.NormPos = PlayfieldCenter * 1
			else:
				Obj.NormPos = Obj.Pos * scaling_factor

			if i >= 2:
				# get rest vectors from between the last 2 positions
				V1:Vector = PrevObject2.NormPos - PrevObject1.NormPos
				V2:Vector = Obj.NormPos - PrevObject1.NormPos
				# get Skalar and Determinant
				dot:float = V1.dot(V2)
				det:float = (V1.x * V2.y) - (V1.y * V2.x)

				# angle is the arc-tangent from both "sites"
				Obj.angle = abs(math.atan2(det, dot))
			else:
				Obj.angle = None

			PrevObject2 = PrevObject1
			PrevObject1 = Obj
			i+=1

	def calcIndividual(self, Difficulty:OsuDifficulty, difftype:int) -> None:
		"""
			difftype 0 = speed
			difftype 1 = aim
			calculates total strain for speed or aim
			at this point, every hitobject must have a normpos
			or overything is going to explode
		"""
		if difftype < 0: raise AttributeError("difftype is needed")
		if not self.Map.hitobjects: raise RuntimeError("there is nothing to calculate")

		# max strains are weighted from highest to lowest.
		# this is how much the weight decays
		DECAY_WEIGHT:float = 0.9

		# NOTE From Francesco149:
		# strains are calculated by analyzing the map in chunks
		# and taking the peak strains in each chunk. this is the
		# length of a strain interval in milliseconds
		strain_step:float = 400.0 * Difficulty.speed_multiplier

		# first object doesn't generate a strain so we begin with
		# an incremented interval end
		interval_end:float = math.ceil(self.Map.hitobjects[0].starttime / strain_step) * strain_step
		max_strain:float = 0.0

		# remember, skip first
		for i, Obj in enumerate(self.Map.hitobjects[1:]):
			PrevObject:OsuHitObject = self.Map.hitobjects[i]

			self.delta_strain(difftype, PrevObject, Obj, Difficulty)

	def deltaStrain(self, difftype:int, PrevObject:OsuHitObject, NowObject:OsuHitObject, Difficulty:OsuDifficulty) -> None:
		"""
			calculates the difftype strain value for a hitobject. stores
			the result in obj.strains[difftype]
			this assumes that normpos is already computed
		"""
		pass
