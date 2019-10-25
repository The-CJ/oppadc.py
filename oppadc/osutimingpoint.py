class OsuTimingPoint(object):
	"""
		representats a timingpoint in osu

		if change is False:
			ms_per_beat = -100.0 * bpm_multiplier

	"""
	def __init__(self, starttime:float or str=0.0, ms_per_beat:float or str=-100.0, change:bool=False):
		self.starttime:float = float(starttime)
		self.ms_per_beat:float = float(ms_per_beat)
		self.change:bool = bool(change)
