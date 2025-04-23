import random
import PIL.Image
try:
    import modules.fltk as fltk,modules.fltk_addons as addons
except ImportError:
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
addons.init(fltk)
from math import ceil

class Solver:
    def __init__(self):
        pass

    def decorate(self, map, freq:float =.5) -> None:
        '''
        Décore automatiquement la carte
        /!\ Ne se sert pas des plages décorables de `modules/plage_deco.py`
            Par soucis de performance, les tuiles éligibles sont réduites aux tuiles unies blanches
                (à savoir `PPPP` et `SSSS`)
            Cependant, une tuile pourra être à cheval avec une autre non unie.
        '''
        # On efface les décos presentes
        map.deco = {}

        visited = set()

        def parcours_zone(x, y, tuile):
            '''
            Partant d'une tuile blanches,
            Détermine la zone de ce même biome
            '''
            zone = []
            s = [(x,y)]
            while s:
                cx, cy = s.pop()
                if (cx, cy) in visited:
                    continue
                visited.add((cx, cy))
                zone.append((cx, cy))

                if map.grille[cy][cx] != tuile:
                    continue

                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < len(map.grille[0]) and 0 <= ny < len(map.grille):
                        if (nx, ny) not in visited and map.grille[ny][nx] == tuile:
                            s.append((nx, ny))

            return zone

        for y, row in enumerate(map.grille):
            for x, tile in enumerate(row):
                if tile == 'PPPP' or tile == 'SSSS':
                    if (x, y) in visited:
                        continue

                    # On détermine la zone de ce biome
                    zone = parcours_zone(x, y, tile)
                    print(zone)
                    aire = len(zone)
                    nb_deco = ceil(aire * freq)
                    for _ in range(nb_deco):
                        dx, dy = random.choice(zone)
                        dx, dy = dx + random.random(), dy + random.random()

                        biome, dec_pos = map.deco_possible(dx, dy)
                        print(dec_pos)
                        if dec_pos:
                            deco = random.choice(dec_pos)
                            map.add_decoration(f"{deco}|{dy}*{dx}")



        

