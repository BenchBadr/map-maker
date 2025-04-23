import random
import PIL.Image
try:
    import modules.fltk as fltk,modules.fltk_addons as addons
except ImportError:
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
addons.init(fltk)

class Solver:
    def __init__(self):
        pass

    def decorate(self, map, proba=.2):
        map.deco = {}
        for y, row in enumerate(map.grille):
            for x in range(len(row)):
                if map.grille[y][x] is None:
                    continue
                if random.randint(0, 10) <= proba:
                    pos = x + random.random(), y + random.random()
                    biome, deco_pos = map.deco_possible(pos[0], pos[1])
                    print(deco_pos)
                    if deco_pos:
                        deco_choice = random.choice(deco_pos)
                        map.add_decoration(deco_choice+'|'+f"{pos[0]}*{pos[1]}")
                        print('added deco',deco_choice, pos)

        return
