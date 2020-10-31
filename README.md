# oppadc.py
osu! performance point and difficulty calculator

This is a rewrite of [oppai-ng](https://github.com/Francesco149/oppai-ng).
All thanks go to @Francesco149

I just rewrite it, because i was bored.
Also i need a object based version so i can use it better in the PhaazeProject

## Install

There are multiple ways, here my "prefered" one:
```
py -m pip install git+https://github.com/The-CJ/oppadc.py.git#egg=oppadc
```

## Example
```py
import oppadc

# there are 3 'main' info sources, all of them are bound to a map

MapInfo = oppadc.OsuMap(file_path="path/to/map.osu")
PP = MapInfo.getPP("HDHR", misses=5, combo=666)
Stats = MapInfo.getStats()
Diff = MapInfo.getDifficulty()

print(f"{MapInfo.artist} - {MapInfo.title} [{MapInfo.version}]")
print(Diff)
print(f"Acc: {round(PP.accuracy, 2)}%")
print(f"Stars: {round(Stats.total, 2)} Stars")
print(f"Gives: {round(PP.total_pp, 1)}pp")
```

```
toby fox + RichaadEB - MEGALOVANIA ~Dual Mix~ [Excors]
<OsuDifficulty ar=10.0 cs=5.2 od=13.44 hp=9.1 mods='HDHR'>
Acc: 99.51%
Stars: 9.69 Stars
Gives: 1167.2pp
```
