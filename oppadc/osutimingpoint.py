class OsuTimingPoint(object):
	"""
		representats a timingpoint in osu

		if change is False:
			ms_per_beat = -100.0 * bpm_multiplier

	"""
	def __init__(self, starttime:float=0.0, ms_per_beat:float=-100.0, change:bool=False):
		self.starttime:float = starttime
		self.ms_per_beat = ms_per_beat
		self.change:bool = change
