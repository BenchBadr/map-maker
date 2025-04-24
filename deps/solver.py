import random
import PIL.Image
try:
    import modules.fltk as fltk,modules.fltk_addons as addons
except ImportError:
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
addons.init(fltk)
from math import ceil

class Solver:
    def __init__(self, map):
        self.map = map
        self.visited = set()
        self.vides = None

    def decorate(self, map = None, freq:float =.5) -> None:
        '''
        Décore automatiquement la carte
        /!\\ Ne se sert pas des plages décorables de `modules/plage_deco.py`
            Par soucis de performance, les tuiles éligibles sont réduites aux tuiles unies blanches
                (à savoir `PPPP` et `SSSS`)
            Cependant, une tuile pourra être à cheval avec une autre non unie.
        '''
        if map is None:
            map = self.map

        # On efface les décos presentes
        map.deco = {}

        # visited = set()

        def parcours_zone(x, y, tuile):
            '''
            Partant d'une tuile blanches,
            Détermine la zone de ce même biome
            '''
            zone = []
            s = [(x,y)]
            while s:
                cx, cy = s.pop()
                if (cx, cy) in self.visited:
                    continue
                self.visited.add((cx, cy))
                zone.append((cx, cy))

                if map.grille[cy][cx] != tuile:
                    continue

                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < len(map.grille[0]) and 0 <= ny < len(map.grille):
                        if (nx, ny) not in self.visited and map.grille[ny][nx] == tuile:
                            s.append((nx, ny))

            return zone

        for y, row in enumerate(map.grille):
            for x, tile in enumerate(row):
                if tile == 'PPPP' or tile == 'SSSS':
                    if (x, y) in self.visited:
                        continue

                    # On détermine la zone de ce biome
                    zone = parcours_zone(x, y, tile)

                    aire = len(zone)
                    nb_deco = ceil(aire * freq)
                    for _ in range(nb_deco):
                        dx, dy = random.choice(zone)
                        dx, dy = dx + random.random(), dy + random.random()

                        biome, dec_pos = map.deco_possible(dx, dy)

                        if dec_pos:
                            deco = random.choice(dec_pos)
                            map.add_decoration(f"{deco}|{dy}*{dx}")


    def empty_tiles(self):
        '''
        Sélectionne les cases vides de la carte
        Optimisé (mémorise d'une utilisation à l'autre)
        '''
        map = self.map
        if not self.vides:
            cases_vides = [(x, y) for y in range(map.dim[0]) for x in range(map.dim[1]) if map.grille[y][x] is None]
            self.vides = cases_vides
        return self.vides
    
    def fill_tile(self, i:int, j:int, tile:str) -> None:
        '''
        Remplace une case vide.
        Args:
            i, j (int): coordonnées de la case
            tile (str): tuile à placer
        '''
        self.map.grille[j][i] = tile
        if self.vides:
            self.vides.remove((i, j))


    def solver(self, map):
        '''
        Résout les conflits de décorations
        '''
        self.map = map

        for i, j in self.empty_tiles():
            tuile_pos = self.map.tuiles_possibles(i, j)
            if tuile_pos:
                tile = random.choice(tuile_pos)
                self.fill_tile(i, j, tile)
        self.decorate()




# juste pour moi
# le sac à dos 

def sac_a_dos(ens, somme):
    if (somme == 0):
        return []
    if (somme < 0):
        return None
    if len(ens) == 0:
        return None
    res = sac_a_dos(ens[1:], somme - ens[0])
    if res is not None:
        res.append(ens[0])
        return res
    else:
        return sac_a_dos(ens[1:], somme)