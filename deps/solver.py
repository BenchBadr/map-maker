import random
import PIL.Image
try:
    import modules.fltk as fltk,modules.fltk_addons as addons
except ImportError:
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
addons.init(fltk)
from math import ceil, floor
import time
class Solver:
    def __init__(self, map):
        self.map = map
        self.visited = set()
        self.vides = None

    def transl_visited(self, tsl):
        '''
        En cas de déplacement de la carte,
        ajuste les coordonnées visitées
        '''
        new_visited = set()
        for i, j in self.visited:
            new_visited.add((i + tsl[0], j + tsl[1]))
        self.visited = new_visited

    def decorate(self, map = None, clear=False, freq:float =.8) -> None:
        '''
        Décore automatiquement la carte
        [!] Ne se sert pas des plages décorables de `modules/plage_deco.py`
            Par soucis de performance, les tuiles éligibles sont réduites aux tuiles unies blanches
                (à savoir `PPPP` et `SSSS`)
            Cependant, une tuile pourra être à cheval avec une autre non unie.
        Args:
            map (Map): carte à décorer (optionnel si fourni ailleurs)
            clear (bool): permet de réinitialiser les décos
            freq (float): fréquence de déco
        '''
        if map is None:
            map = self.map

        # On ne garde que les décos placées au préalable
        # de façon automatique

        if clear:
            self.visited = set()
            map.deco = {}
            map.tiles_to_deco = {}

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

                        biome, dec_pos = map.deco_possible(dy, dx)

                        if dec_pos:
                            deco = random.choice(dec_pos)
                            map.add_decoration(f"{deco}|{dy}*{dx}")


    def empty_tiles(self) -> list[tuple[int, int, int]]:
        '''
        Sélectionne les cases vides de la carte, triées par nombre de tuiles possibles (plus contrainte en premier).
        Optimisé avec mise en cache des cases vides et de leurs contraintes.
        De plus, tri la liste en fonction du nombre de contraintes
        Returns:
            list: Liste de tuples (x, y, nb_possibles) triée par nb_possibles croissant.
        '''
        map = self.map
        if self.vides is None:
            # TODO : Memo `tuiles_possibles` (tâche 4.1.4)
            cases_vides = []
            for y in range(map.dim[0]):
                for x in range(map.dim[1]):
                    if map.grille[y][x] is None:
                        nb_possibles = len(map.tuiles_possibles(x, y))
                        cases_vides.append((x, y, nb_possibles))
            # Tri croissant de contraintes (moins il y a de tuiles plus c'est contraint)
            cases_vides.sort(key=lambda t: t[2])
            self.vides = cases_vides
        return self.vides


    def solver(self, map, vides = None, draw = None) -> bool:
        '''
        Résout les conflits de décorations
        Args:
            map (Map): carte à résoudre
        Returns:
            bool: True si la carte est résolue, False sinon
                Permet par la suite l'affichage 'dune erreur 
                si les contraintes ne permettent pas de résolution.
        '''
        self.vides = None
        self.map = map
        if vides is None:
            self.empty_tiles()
        else:
            self.vides = vides

        def backtrack(vides):
            # Solution trouvée
            if not vides:
                return True

            # choix optimal (par constructions de `vides`)
            i, j, ct = vides[0]

            dpm = self.map.deplacement_map
            tuiles_pos = self.map.tuiles_possibles(i+dpm[1], j+dpm[0])

            if not tuiles_pos:
                return False
            
            random.shuffle(tuiles_pos)

            for tuile in tuiles_pos:
                
                self.map.grille[j][i] = tuile

                # visualisation (optionnelle, si en mode debug)
                if self.map.debug and draw is not None:
                    time.sleep(.01)
                    print(f"{round((1 - len(vides)/len(self.vides))*100,2)}%")
                    draw()

                if backtrack(vides[1:]):
                    return True
                
                # inutile — reaffecté au debut
                # self.map.grille[j][i] = None
                

            return False

        if self.vides:
            r = backtrack(self.vides.copy())
            self.decorate()
            if not r:
                return False
            self.vides = []
        
        return True




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