from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .osumap import OsuMap

import math
from .vector import Vector
from .osudifficulty import OsuDifficulty
from .osuobject import OsuHitObject, OSU_OBJ_SPINNER, OSU_OBJ_CIRCLE, OSU_OBJ_SLIDER
from .osumod import OsuModIndex

DIFF_SPEED:int = 0
DIFF_AIM:int = 1

# strain stuff
DECAY_BASE:list = [ 0.3, 0.15 ] # strain decay per interval
WEIGHT_SCALING:list = [ 1400.0, 26.25 ] # balances speed and aim

# spacing weight stuff
MIN_SPEED_BONUS:int = 75 # ~200BPM 1/4 streams
MAX_SPEED_BONUS:int = 45 # ~330BPM 1/4 streams
ANGLE_BONUS_SCALE:int = 90
AIM_TIMING_THRESHOLD:int = 107
SPEED_ANGLE_BONUS_BEGIN:float = 5 * math.pi / 6
AIM_ANGLE_BONUS_BEGIN:float = math.pi / 3
SINGLE_SPACING:int = 125 # arbitrary thresholds to determine when a stream is spaced enough that it becomes hard to alternate

class OsuStats(object):
	"""
		contains everything to calculate star rating and more
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
		return f"<{self.__class__.__name__} stars={round(self.total, 2)} (aim={round(self.aim, 2)} speed={round(self.speed, 2)})>"

	def __str__(self) -> str:
		return self.__repr__()

	def calc(self, singletap_threshold:int=125) -> None:
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
		Difficulty:OsuDifficulty = self.Map.getDifficulty()

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

		# tempraly stars diff
		self.speed = speed[0]
		self.aim = aim[0]

		self.speed_difficulty = speed[1]
		self.aim_difficulty = aim[1]

		self.aim_length_bonus = self.lengthBonus(self.aim, self.aim_difficulty)
		self.speed_difficulty = self.lengthBonus(self.speed, self.speed_difficulty)

		# actully star count
		self.aim = math.sqrt(self.aim) * STAR_SCALING_FACTOR
		self.speed = math.sqrt(self.speed) * STAR_SCALING_FACTOR

		# punish all touchscreen user
		if Difficulty.mods_value & OsuModIndex.getValueFromString("TD"):
			self.aim = self.aim ** 0.8

		# set total stars
		self.total = self.aim + self.speed
		# add extreme
		self.total += abs(self.speed - self.aim) * EXTREME_SCALING_FACTOR

		# single taps stats... do i need this? mm who cares
		for i, Obj in enumerate(self.Map.hitobjects[1:]):
			PrevObject:OsuHitObject = self.Map.hitobjects[i]

			Obj:OsuHitObject = Obj

			if Obj.is_single:
				self.amount_singles += 1

			if not Obj.osu_obj & (OSU_OBJ_CIRCLE | OSU_OBJ_SLIDER):
				continue

			interval:float = (Obj.starttime - PrevObject.starttime) - Difficulty.speed_multiplier

			if interval >= singletap_threshold:
				self.amount_singles_threshold += 1

	def lengthBonus(self, stars:float, diff:float) -> float:
		return 0.32 + ( 0.5 * (math.log10(diff + stars) - math.log10(stars)) )

	def calcNormPos(self, PlayfieldCenter:Vector, scaling_factor:float) -> None:
		PrevObject1:OsuHitObject = None
		PrevObject2:OsuHitObject = None
		i:int = 0
		for Obj in self.Map.hitobjects:
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

	def calcIndividual(self, Difficulty:OsuDifficulty, difftype:int) -> tuple:
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

		# reset before 2nd, calc
		self.strains = []

		# first object doesn't generate a strain so we begin with
		# an incremented interval end
		interval_end:float = math.ceil(self.Map.hitobjects[0].starttime / strain_step) * strain_step
		max_strain:float = 0.0

		# remember, skip first
		for i, NowObject in enumerate(self.Map.hitobjects[1:]):
			PrevObject:OsuHitObject = self.Map.hitobjects[i]

			# calculate all strains for all objects
			self.deltaStrain(difftype, PrevObject, NowObject, Difficulty)

			while NowObject.starttime > interval_end:
				# add max strain for this interval
				self.strains.append(max_strain)

				# decay last object's strains until the next
				# interval and use that as the initial max strain
				decay = pow(
					DECAY_BASE[difftype],
					(interval_end - PrevObject.starttime) / 1000.0
				)

				max_strain = PrevObject.strains[difftype] * decay
				interval_end += strain_step

			max_strain = max(max_strain, NowObject.strains[difftype])

		# re-add last strain
		self.strains.append(max_strain)

		# weight the top strains sorted from highest to lowest
		weight:float = 1.0
		total:float = 0.0
		difficulty:float = 0.0

		self.strains.sort(reverse=True)

		for strain in self.strains:
			total += pow(strain, 1.2)
			difficulty += strain * weight
			weight *= DECAY_WEIGHT

		return ( difficulty, total )

	def deltaStrain(self, difftype:int, PrevObject:OsuHitObject, NowObject:OsuHitObject, Difficulty:OsuDifficulty) -> None:
		"""
			calculates the difftype strain value for a hitobject.
			stores
			the result in obj.strains[difftype]
			this assumes that normpos is already computed
		"""

		value:float = 0.0
		time_elapsed:float = (NowObject.starttime - PrevObject.starttime) / Difficulty.speed_multiplier
		NowObject.delta_time = time_elapsed
		decay:float = (DECAY_BASE[difftype]) ** (time_elapsed/1000)

		# this implementation doesn't account for sliders
		# Note from me to Francesco149: sliders? do you mean spinners?
		if NowObject.osu_obj & ( OSU_OBJ_SLIDER | OSU_OBJ_CIRCLE):
			distance:float = (NowObject.NormPos - PrevObject.NormPos).length
			NowObject.delta_distance = distance

			value, is_single = self.deltaSpacingWeight(
				difftype,
				NowObject.delta_distance, NowObject.delta_time,
				PrevObject.delta_distance, PrevObject.delta_time,
				NowObject.angle
			)

			value *= WEIGHT_SCALING[difftype]

			# we found out the object is a single type, so we set it
			if difftype == DIFF_SPEED:
				NowObject.is_single = is_single

		NowObject.strains[difftype] = (PrevObject.strains[difftype] * decay) + value

	def deltaSpacingWeight(self, *x) -> tuple:
		# NOTE: everything happening in this part... is to high for me
		# i don't really understand it, maybe because i never looked into the details,
		# or the wiki how everything is calculated. Im sure it can be looked up somewhere, i don't know
		# Or because im dumb ¯\_(ツ)_/¯
		# By the way, once again for Francesco149 for already searching all calculations together

		if x[0] == DIFF_AIM:
			return self.deltaSpacingWeightAim(*x)

		elif x[0] == DIFF_SPEED:
			return self.deltaSpacingWeightSpeed(*x)

		else:
			raise NotImplementedError()

	def deltaSpacingWeightAim(self, difftype:int, delta_distance:float, delta_time:float, prev_delta_distance:float, prev_delta_time:float, angle:float) -> tuple:

		strain_time:float = max(delta_time, 50.0)
		prev_strain_time:float = max(prev_delta_time, 50.0)

		result:float = 0.0

		# aim angle bonus
		if angle != None and angle > AIM_ANGLE_BONUS_BEGIN:
			angle_bonus:float = math.sqrt(
				max(prev_delta_distance - ANGLE_BONUS_SCALE, 0.0) *
				pow(math.sin(angle - AIM_ANGLE_BONUS_BEGIN), 2.0) *
				max(delta_distance - ANGLE_BONUS_SCALE, 0.0)
			)
			result = 1.5 * pow(max(0.0, angle_bonus), 0.99) / max(AIM_TIMING_THRESHOLD, prev_strain_time)

		weighted_distance = pow(delta_distance, 0.99)
		res:float = max(
			( result + weighted_distance / max(AIM_TIMING_THRESHOLD, strain_time) ),
			( weighted_distance / strain_time )
		)
		return (res, False)

	def deltaSpacingWeightSpeed(self, difftype:int, delta_distance:float, delta_time:float, prev_delta_distance:float, prev_delta_time:float, angle:float) -> tuple:

		strain_time:float = max(delta_time, 50.0)

		is_single:bool = delta_distance > SINGLE_SPACING
		delta_distance = min(delta_distance, SINGLE_SPACING)
		delta_time = max(delta_time, MAX_SPEED_BONUS)

		speed_bonus:float = 1.0
		if delta_time < MIN_SPEED_BONUS:
			speed_bonus += ( (MIN_SPEED_BONUS - delta_time) / 40 ) ** 2

		angle_bonus:float = 1.0
		angle_bonus_part:float = 0.0
		if angle != None and angle < SPEED_ANGLE_BONUS_BEGIN:
			sin:float = math.sin( 1.5 * (SPEED_ANGLE_BONUS_BEGIN - angle) )
			angle_bonus += (sin * sin / 3.57)

			if angle < math.pi / 2:
				angle_bonus = 1.28

				if delta_distance < ANGLE_BONUS_SCALE and angle < (math.pi / 4):
					angle_bonus_part = (1 - angle_bonus)
					angle_bonus_part *= min( (ANGLE_BONUS_SCALE - delta_distance) / 10, 1 )
					angle_bonus += angle_bonus_part
				elif delta_distance < ANGLE_BONUS_SCALE:
					angle_bonus_part = (1 - angle_bonus)
					angle_bonus_part *= min( (ANGLE_BONUS_SCALE - delta_distance) / 10, 1 )
					angle_bonus_part *= math.sin((math.pi / 2.0 - angle) * 4.0 / math.pi)
					angle_bonus += angle_bonus_part

		res:float = (1 + (speed_bonus - 1) * 0.75)
		res *= angle_bonus
		res *= (0.95 + speed_bonus * pow(delta_distance / SINGLE_SPACING, 3.5))
		res /= strain_time

		return (res, is_single)
