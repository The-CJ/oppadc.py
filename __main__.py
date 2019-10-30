import sys
from oppadc import OsuMap, OsuModIndex
from oppadc.osudifficulty import OsuDifficulty
from oppadc.osustats import OsuStats
from oppadc.osupp import OsuPP

mods:int = 0
acc_percent:float = 100.0
combo:int = None
misses:int = 0

for arg in sys.argv:
	if arg.startswith("+"):
		mods = OsuModIndex.getValueFromString(arg[1:])
	elif arg.endswith("%"):
		acc_percent = float(arg[:-1])
	elif arg.endswith("x"):
		combo = int(arg[:-1])
	elif arg.endswith("m"):
		misses = int(arg[:-1])

map_path_str:str = sys.argv[1]

Map:OsuMap = OsuMap(file_path=map_path_str)

P:OsuPP = Map.getPP(Mods=mods, accuracy=acc_percent, combo=combo, misses=misses)
D:OsuDifficulty = Map.getDifficulty()
S:OsuStats = Map.getStats()

print("#"*32)
print("--General--")
print(f"{Map.artist} - {Map.title} [{Map.version}]")
print(f"Mods: {OsuModIndex.getStringFromValue(D.mods_value)}")
print(f"OD: {round(D.od,1)} AR: {round(D.ar,1)} CS: {round(D.cs,1)} HP: {round(D.hp,1)} ")
print("--Stats--")
print(f"Stars: {round(S.total,2)} (aim={round(S.aim,2)} speed={round(S.speed,2)})")
print(f"Combo: {P.combo} / {Map.maxCombo()} ({P.misses} misses)")
print(f"Acc: {round(P.accuracy,2)}% / 100%")
print("--PP--")
print(f"{round(P.total_pp,2)}PP (speed={round(P.speed_pp,2)} aim={round(P.aim_pp,2)} acc={round(P.acc_pp,2)})")
print("#"*32)



