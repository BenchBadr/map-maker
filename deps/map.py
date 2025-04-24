import PIL.Image
try:
    from cree_dico import cree_dico
    from modules.plage_deco import analyse_tuile
    import modules.fltk as fltk,modules.fltk_addons as addons
except ImportError:
    from deps.cree_dico import cree_dico, cree_deco
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
    from deps.modules.plage_deco import analyse_tuile
addons.init(fltk)
from math import floor, ceil

class Map:
    def __init__(self, grille=None, deco={}, tiles_to_deco={}) -> None:
        """
        Initialise la carte avec une grille donnée.
        Args:
            grille: La grille représentant la carte.
        """
        if grille is None:
            # Crée une grille vide de 10x10
            self.grille = [[None for _ in range(2)] for _ in range(2)]
        else:
            self.grille = grille

        self.dim = len(self.grille), len(self.grille[0])
        import os
        self.tuiles = cree_dico('deps/assets/tuiles')
        self.deco_tiles = cree_deco('deps/assets/decors')


        # used for tile picker
        self.current_page = 0
        self.deplacement_map = (0,0)
        self.debug = False
        self.riviere = False

        # memo deco plage décorable
        self.plage_memo = {}
        # stockage des decos de la map
        self.deco = deco
        # obtenir deco associée a tuiles (deletion...)
        self.tiles_to_deco = tiles_to_deco
        # memo des tuiles
        self.deco_memo = None

    def dump_img(self, path) -> PIL.Image:
        """
        Renvoie une image représentant la carte.
        Prend soin de ne pas la recréer s'il  suffit de faire des modifications.
        Returns:
            image: L'image représentant la carte.
        """
        x, y = self.dim
        image = PIL.Image.new('RGB', (x*100, y*100), color=(255, 255, 255))
        for i in range(x):
            for j in range(y):
                tuile = self.grille[i][j]
                if tuile is not None:
                    image.paste(PIL.Image.open(self.tuiles[tuile]), (i*100, j*100))
                else:
                    # Créer une case blanche si la tuile est None
                    white_square = PIL.Image.new('RGB', (100, 100), color=(128, 128, 128))
                    image.paste(white_square, (i*100, j*100))

        # Add decors
        for coords, (path_dec, ims) in self.deco.items():
            coords = (ceil(coords[0] * 100), ceil(coords[1] * 100))
            deco_image = PIL.Image.open(path_dec)
            image.paste(deco_image, coords)
        image.save(path)
        return image
    
    def edit_tile(self, i:int, j:int, tuile:str) -> None:
        """
        Modifie la tuile à la position (i, j) de la grille.
        Args:
            i: La coordonnée i de la tuile.
            j: La coordonnée j de la tuile.
            tuile: Le nom de la nouvelle tuile.
        """

        # Ajuster les coordonnés en fonction du déplacement
        i, j = i - self.deplacement_map[0], j - self.deplacement_map[1]

        # Redimension dynamique et invisible, pour "estomper" la finitude temporaire de la carte

        tsl = [0,0] # translation si redimensionnement

        if i < 0:
            self.grille = [[None for _ in range(self.dim[1])] for _ in range(-i)] + self.grille
            tsl[0] = -i
            i = 0
        elif i >= self.dim[0]:
            self.grille += [[None for _ in range(self.dim[1])] for _ in range(i - self.dim[0] + 1)]
        if j < 0:
            for k in range(len(self.grille)):
                self.grille[k] = [None for _ in range(-j)] + self.grille[k]
            tsl[1] = -j
            j = 0
        elif j >= self.dim[1]:
            for k in range(len(self.grille)):
                self.grille[k] = self.grille[k] + [None for _ in range(j - self.dim[1] + 1)]

        self.dim = (len(self.grille), len(self.grille[0]))
        self.grille[i][j] = tuile

        # Si on doit translater les coords,
        # On ajuste les decos

        if tsl != [0,0]:

            deco_back = self.deco.copy()
            tiles_to_deco_back = self.tiles_to_deco.copy()
            self.deco = {}
            self.tiles_to_deco = {}
            # On ajuste les tiles_to_deco
            for tile_deco, coords_list in tiles_to_deco_back.items():
                new_co_list = []
                for coords in coords_list:
                    new_coords = (coords[0] + tsl[0], coords[1] + tsl[1])
                    self.deco[new_coords] = deco_back[coords]
                    new_co_list.append(new_coords)
                new_tile = (tile_deco[0] + tsl[0], tile_deco[1] + tsl[1])
                self.tiles_to_deco[new_tile] = new_co_list

        # Si suppression de tuile
        # Supprimer les décos associée
        if tuile is None:
            if (i, j) in self.tiles_to_deco:
                for coords in self.tiles_to_deco[(i, j)]:
                    del self.deco[coords]
                del self.tiles_to_deco[(i, j)]

        return (j + self.deplacement_map[1], i + self.deplacement_map[0]), tsl

    def display_map(self, unit, c0, c1, zoom = 1, deplacement_map = (0,0)) -> None:
        """
        Affiche la carte par cases d'images (ou rectangles si case non définies)

        Args:
            unit: La taille de chaque case.
            c0: La coordonnée x de la carte.
            c1: La coordonnée y de la carte.
            zoom: Le facteur de zoom.
            deplacement_map: Le déplacement de la carte (utilisé pour le scrolling)
        """

        # TODO : Avoid unnecessary renders (case of overflow)

        unit = floor(unit * zoom)
        c0 = (c0 - (unit*self.dim[0]) // 2 +unit // 2) + deplacement_map[0] * unit
        c1 = (c1 - (unit*self.dim[1]) // 2 + unit // 2) + deplacement_map[1] * unit
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if self.grille[i][j] is not None:
                    fltk.image(c0+i*unit, 
                            c1+j*unit, 
                            self.tuiles[self.grille[i][j]], 
                            hauteur=unit, 
                            largeur=unit)
                    if self.debug:
                        taille = unit // 8
                        fltk.rectangle(c0+i*unit - taille*2,
                                c1+j*unit - taille, 
                                c0+i*unit + taille*2, 
                                c1+j*unit + taille*.75, 
                                remplissage='beige', 
                                couleur='orange',
                                epaisseur=0)
                        fltk.texte(c0+i*unit - taille * 2,
                            c1+j*unit - taille, self.grille[i][j], taille = taille, couleur='orange')
                else:
                    fltk.rectangle(c0+(i-1/2)*unit, 
                            c1+(j - 1/2)*unit, 
                            c0+(i + 1/2)*unit, 
                            c1+(j + 1/2)*unit, 
                            remplissage='#555' if self.debug else 'grey', # Change this color to make Map boundaries visible
                            epaisseur=0)
                    
        # Display decorations
        init = c0 - unit * .5, c1 - unit * .5
        for coords, (path, ims) in self.deco.items():
            coords = ((coords[0] + ims[0]*.5) * unit, (coords[1] + ims[1]*.5) * unit)
            fltk.image(init[0] + coords[0], init[1] + coords[1], path,
                       hauteur = floor(ims[1] * unit),
                       largeur = floor(ims[0] * unit))
                    

    def tuiles_selector(self, key:str, x:int, y:int, x2:int, y2:int, args_func:dict) -> None:
        """
        Dessine la grille de sélection des tuiles.

        Args:
            key: La clé de la fenêtre
            (x,y,x2,y2): Les coordonnées de la fenêtre de dessin (du rectangle de la main area)
            args_func: dictionnaire passant les arguments de la fonction, ici, utilisé pour obtenir le tile selectionné
        """
        tile = args_func['tile']
        tile_memo = args_func['tile_memo']

        # Get possible tiles properly
        neigh = [[t, self.tuiles[t]] for t in self.tuiles_possibles(tile[0], tile[1])]
        s = len(neigh)
        w, h = abs(x - x2), abs(y - y2)
        unit = min(w, h) // 10
        p = unit // 2

        n_x = floor((w + p) // (unit + p))
        n_y = floor((h + p) // (unit + p))

        pages = ceil(s / (n_x * n_y))

        if pages == 0:
            c2 = x, y
            sub_page = x2 - x, y2 - y
            a, b, r = c2[0] + sub_page[0] // 2, c2[1] + sub_page[1] // 2, min(sub_page)//4
            # Texte
            t1 = 'Placement impossible'
            t2 = 'Supprimez des tuiles puis réessayez'

            taille1 = int((5*r)//len(t1))
            taille2 = int((5*r)//len(t2))

            fltk.texte(a - taille1 * len(t1) * .3, b - taille1,  t1, couleur='white', tag=key, taille=taille1)
            fltk.texte(a - taille2 * len(t2) * .3, b + taille1, t2, couleur='#888', tag=key, taille=taille2)
            return

        self.current_page = min(max(0,self.current_page), pages - 1)
        current_page = self.current_page

        """
        Définition pour le changement de variables (comme dans les sommes en maths ou l'on remplace k...)
        Par du principe que si la page n'est pas la première alors toute les précédentes étaient pleines.
        Fonctionnement attendu puisque passer à la page suivant avec une page précédente non pleine donne une fenêtre vide.
        """

        count = (current_page * (n_x * n_y))

        # display scrollbar (only if there is multiple pages)
        h_scrollbar = abs(y - y2) + p
        thumb_height = h_scrollbar * (1/pages)

        # Draw the scrollbar accordingly with the current ratio
        if pages > 1:
            ## Scrollbar background
            fltk.rectangle(x2 + p // 2, y + p, x2+p*1.25, y + h_scrollbar, tag=key, remplissage='#444')
            ## Scrollbar thumb
            fltk.rectangle(x2 + p // 2, 
                        y + p + (current_page) * thumb_height, 
                        x2+p*1.25, 
                        y + thumb_height * (current_page + 1), 
                        tag=key, 
                        remplissage='grey')

        # changement de variables pour afficher une page différente
        for i in range(n_y):
            for j in range(min(n_x, s - count)):
                c = (x+j*(unit+p), y+(i)*(unit+p)+p*2)
                tile_memo.add(neigh[count][0])
                fltk.image(c[0], c[1], neigh[count][1], hauteur=int(unit), largeur=int(unit), tag='tile_'+neigh[count][0])
                count += 1

    def emplacement_valide(self, i: int,j: int, nom_tuile: str) -> bool:
        """
        Vérifie si un emplacement est valide en fonction de la tuile.

        Args:
            i: Indice i à vérifier.
            j: Indice j à vérifier.
            nom_tuile: Nom de la nouvelle tuile à vérifier.
        Returns:
            bool: True ou False en fonction de si la nouvelle tuile est plaçable ou non.
        """
        # Tâche 1
        ## Vérification des raccords
        rows, cols = self.dim

        ### (dr, dc, index_voisin, index_tuile) tels que
        ### dr, dc = vect de déplacement (0,-1) <=> case du haut
        ### index_voisin, index_tuile = indices des côtés adjacents (à comparer)
        neighbor_checks = [
            # Vertical
            (-1, 0, 2, 0),
            ( 1, 0, 0, 2), 

            # Horizontal
            ( 0, 1, 3, 1),
            ( 0,-1, 1, 3) 
        ]

        for dr, dc, index_voisin, index_tuile in neighbor_checks:
            ni, nj = i + dr, j + dc

            # Ignore les voisins en dehors de la grille
            if not (0 <= nj < rows and 0 <= ni < cols):
                continue

            voisin = self.grille[nj][ni]

            # si non défini, pas de contrainte
            if voisin is not None:
                if voisin[index_voisin] != nom_tuile[index_tuile]:
                    return False 
        if self.riviere and 'R' in nom_tuile:
            return self.riviere_valide(i, j, nom_tuile)
        return True
    
    def get_vois(self, i:int,j:int, tested:tuple, nom_tuile:str) -> list[tuple[int,int]]:
        '''
        Renvoie les cases voisines où se poursuit la rivière
        > [!warn] Utilisé spécifiquement pour les rivières.
        '''
        dir =  [
            # Vertical
            (-1, 0, 2),
            ( 0, 1, 3),
            ( 1, 0, 0),
            (0, -1 ,1) 
        ]

        # TODO : Mémoiser l'obtention des voisins

        voisins = []

        if nom_tuile is None:
            return []
        
        # tuile actuelle
        if (i, j) == tested:
            tuile_act = nom_tuile
        else:
            tuile_act = self.grille[j][i]

        if tuile_act is None:
            return []

        for index_tuile, (dc, dr, index_voisin) in enumerate(dir):
            ni, nj = i + dc, j + dr

            # Ignore les voisins en dehors de la grille (car <=> None)
            if 0 <= ni < self.dim[1] and 0 <= nj < self.dim[0]:

                # valeur théorique non réduite au tile actuel
                if (ni, nj) == tested:
                    voisin = nom_tuile
                else:
                    voisin = self.grille[nj][ni]


                if voisin is None:
                    continue


                
                # Ici, on check la correspondance de biômes adjacents
                # Mais specifiquement pour R
                if voisin[index_voisin] == 'R':
                    if tuile_act[index_tuile] == voisin[index_voisin]:
                        voisins.append((ni, nj))

        return voisins


    def riviere_valide(self, i:int, j:int, nom_tuile:str) -> bool:
        """
        Renvoie le nombre d'extremités / sources / mers de la rivière en fonction du parcours
        Si pas de voisin <=> fin (ou début) de rivière
        Il doit s'agir, au choix de:
        1. mer (fin)
        2. montagne (début)
        3. une case aux extrémités de la grille (fin)
            3.1. None <=> Extremité
        """

        parcours = []
        graph_riv = self.riviere_parcours(i, j, nom_tuile, parcours)

        if graph_riv is False:
            # On exclut les boucles
            return False
        
        if len(parcours) == 1:
            return True

        def analyse_ext(coords:tuple) -> tuple[int, int, int]:
            """
            Vérifie si la tuile actuelle se conforme à l'un des 3 cas susmentionnés
            Args:
                coords: Coordonnées de la case
            Returns:
                (x,y,z)
                x : mer
                y : montagne
                z : extremité
            """

            ni, nj = coords

            # Définir en prenant en compte le tile de test
            if coords == (i, j):
                tile = nom_tuile
            else:
                tile = self.grille[nj][ni]

            dir = [(-1, 0),( 0, 1),( 1, 0),( 0,-1)]
            deg_idc = [i for i,c in enumerate(tile) if c == 'R']

            # Compte
            if 'M' in tile:
                return (2, 1)
            elif 'G' in tile or 'H' in tile or 'B' in tile or 'D' in tile:
                return (1, 1)
            
            elif (ni == 0 or ni == self.dim[0] - 1 or nj == 0 or nj == self.dim[1] - 1) and \
                 ((ni == 0 and 0 in deg_idc) or \
                  (ni == self.dim[0] - 1 and 2 in deg_idc) or \
                  (nj == 0 and 3 in deg_idc) or \
                  (nj == self.dim[1] - 1 and 1 in deg_idc)):
                # S'assure que la riviere se prolonge en dehors de la carte
                # Exclut de fait les cas comme des virages
                    return (3, 1)
            else:
                # Cas 3.1
                # Si la riviere se prolonge en des None
                for idc in deg_idc:

                    if (ni + dir[idc][0], nj + dir[idc][1]) == (i,j):
                        continue # On ne teste jamais avec None
                    if 0 <= nj + dir[idc][1] < self.dim[0] and 0 <= ni + dir[idc][0] < self.dim[1]:
                        if self.grille[nj + dir[idc][1]][ni + dir[idc][0]] is None:
                            return (3, 1)
            return False
        
        acc_global = [0,0,0]
        for case in parcours:
            acc_case = analyse_ext(case)
            if acc_case:
                acc_global[acc_case[0] - 1] += acc_case[1]


        m, M = min(acc_global[0], acc_global[1]), max(acc_global[0], acc_global[1])
        ext = acc_global[2]

        if not(m == 0 and M == 0):
            if M > m + ext:
                return False

        # def remontee_etat(start:tuple):
        #     acc = analyse_ext(start)
        #     if start not in graph_riv:
        #         # pas de parents
        #         return acc
        #     acc = analyse_ext(start)
        #     for parent in graph_riv[start]:
        #         acc_parent = remontee_etat(parent)
        #         acc = (acc[0] + acc_parent[0], acc[1] + acc_parent[1], acc[2] + acc_parent[2])
        #     return acc

                

        return True
        


    def riviere_parcours(self, i:int, j:int, nom_tuile:str, parcours:list) -> bool:
        '''
        Parcours en profondeur de la rivière
        Vérifie par la même occasion si contient des boucles.
        '''
        visited = set()
        s = [((i, j), None)]
        graph_riv = {}
        while s:
            tile, parent = s.pop()

            if parent:
                if tile not in graph_riv:
                    graph_riv[tile] = []
                graph_riv[tile].append(parent)

            ti, tj = tile
            
            if tile not in visited:
                visited.add((ti, tj))

            parcours.append((ti, tj))

            voisins = self.get_vois(ti, tj, (i,j), nom_tuile)

            for voisin in voisins:
                if voisin not in visited:
                    s.append((voisin, tile))
                elif voisin != parent:
                    return False
        return graph_riv



    
    def tuiles_possibles(self, i:int, j:int) -> list:
        """
        Ajoute les options des tuiles disponibles dans la case en fonction de toutes les tuiles.

        Args:
            grille : Grille du MapMaker.
            i : Indice i à vérifier.
            j : Indice j à vérifier.
            list_tuiles : Liste de toutes les tuiles disponibles.
        Returns:
            options (list) : Liste contenant les tuiles possibles.
        """
        options = []
        for tuile in self.tuiles.keys():
            # Prend soin d'ajuster en fonction du déplacement
            if self.emplacement_valide(i - self.deplacement_map[1], j - self.deplacement_map[0], tuile):
                options.append(tuile)
        return options
    
    def deco_selector(self, key, x, y, x2, y2, args_func:dict) -> None:
        """
        Dessine la grille de sélection des tuiles.

        Args:
            key: La clé de la fenêtre
            (x,y,x2,y2): Les coordonnées de la fenêtre de dessin (du rectangle de la main area)
            args_func: dictionnaire passant les arguments de la fonction, ici, utilisé pour obtenir le tile selectionné
        """
        coords = args_func['coords']
        zoom, dep_map = args_func['state']

        h, w = fltk.hauteur_fenetre(), fltk.largeur_fenetre()
        dim = self.dim
        size = min(w, h)
        unit = floor(size//max(dim) * zoom)

        grid_width = dim[0] * unit
        grid_height = dim[1] * unit

        base_x = (w - grid_width) // 2
        base_y = (h - grid_height) // 2

        coords = (coords[0] - base_x, coords[1] - base_y)
        coords = (coords[0]/unit - dep_map[0], coords[1]/unit - dep_map[1])

        if self.deco_memo is None:
            self.deco_memo = self.deco_possible(coords[0], coords[1]), coords
        
        # Éviter de reexecuter à chaque redessin
        (biome, deco_possibles), _c = self.deco_memo

        if len(deco_possibles) == 0:
            c2 = x, y
            sub_page = x2 - x, y2 - y
            a, b, r = c2[0] + sub_page[0] // 2, c2[1] + sub_page[1] // 2, min(sub_page)//4
            # Texte
            t1 = 'Pas de décoration'
            t2 = 'Aucun décor n\'est disponible pour cette position.'

            taille1 = int((5*r)//len(t1))
            taille2 = int((5*r)//len(t2))

            fltk.texte(a - taille1 * len(t1) * .3, b - taille1,  t1, couleur='white', tag=key, taille=taille1)
            fltk.texte(a - taille2 * len(t2) * .3, b + taille1, t2, couleur='#888', tag=key, taille=taille2)
            return

    
        # Dessin des possibles
        s = len(deco_possibles)
        win_w, win_h = abs(x - x2), abs(y - y2)
        scale = 3
        win_unit = min(win_w, win_h) // scale
        win_p = win_unit // 2 

        n_x = floor((win_w + win_p) // (win_unit + win_p))
        n_y = floor((win_h + win_p) // (win_unit + win_p))

        pages = ceil(s / (n_x * n_y))
        self.current_page = min(max(0,self.current_page), pages - 1)
        current_page = self.current_page


        # draw the scrollbar
        h_scrollbar = abs(y - y2)
        thumb_height = h_scrollbar * (1/pages)
        if pages > 1:
            ## Scrollbar background
            fltk.rectangle(x2, y + win_p // 5, x2 + win_p // 5, y + h_scrollbar + win_p // 5, tag=key, remplissage='#444')
            ## Scrollbar thumb
            fltk.rectangle(x2, 
                        y + (current_page) * thumb_height + win_p // 5, 
                        x2 + win_p // 5, 
                        y + thumb_height * (current_page + 1) + win_p // 5, 
                        tag=key, 
                        remplissage='grey')
            
        # changement de variables pour afficher une page différente
        count = (current_page * (n_x * n_y))
        for i in range(n_y):
            for j in range(min(n_x, s - count)):
                c = (x+j*(win_unit+win_p), y+(i)*(win_unit+win_p)+win_p/2.5)

                deco = deco_possibles[count]

                tag = 'decor_'+deco+'|'+f"{coords[0]}*{coords[1]}"

                path, size_deco = self.deco_tiles[biome][deco]
                pad_img = win_unit * .5, win_unit * .5 #* (size_deco[1])#win_unit*(.5*(1 - size_deco[0] *.5)), win_unit*(.5*(1 - size_deco[1] * .5))

                fltk.rectangle(c[0], c[1], c[0] + win_unit, c[1] + win_unit, remplissage='#777', epaisseur=0, tag=tag)
                fltk.image(c[0]+pad_img[0], c[1]+pad_img[1], path, 
                        hauteur=ceil(size_deco[1] * win_unit), largeur=ceil(size_deco[0] * win_unit), 
                        tag=tag)
                count += 1

    def deco_possible(self,  x:float, y:float) -> list:
        """
        Renvoie les décorations possibles pour une tuile donnée.

        Args:
            x: Coordonnée x de la tuile.
            y: Coordonnée y de la tuile.
        Returns:
            list: Liste des décorations possibles.
        """

        def test_rectangle(tuile:str, start:tuple, end:tuple) -> list:
            """
            Test si un rectangle peut être placée sur la tuile.
            Ce rectangle est soit un placement complet d'un decor
            Soit partiel si la tuile est à cheval.

            Args:
                tuile: str, nom de la tuile
                start: tuple, coord de debut du rectangle
                end: tuple, coord de fin du rectangle
            Returns:
                bool: placement valide
            """
            if tuile is None:
                return False
            
            if tuile not in self.plage_memo:
                self.plage_memo[tuile] = analyse_tuile(tuile)

            bboxes = self.plage_memo[tuile]

            x1, y1 = start
            x2, y2 = end

            for bbox in bboxes:
                bx_min, by_min, bx_max, by_max = bbox
                if (x1 <= bx_max and x2 >= bx_min and
                    y1 <= by_max and y2 >= by_min):
                    return False
            return True
        
        # Les tuiles sont toutes plus petites, 
        # donc une deco sera au plus sur deux tuiles si décalée
        source = (floor(x), floor(y))
        tuile_source = self.grille[source[0]][source[1]]

        if tuile_source is None:
            return None, []

        if 'P' in tuile_source:
            eligible = self.deco_tiles['terre']
            biome = 'terre'
        elif tuile_source == 'SSSS':
            eligible = self.deco_tiles['mer']
            biome = 'mer'
        else:
            return None, []

        deco_ok = []

        for candidat in eligible:

            # memo dimensions decor
            if self.deco_tiles[biome][candidat][1] is None:
                img = PIL.Image.open(eligible[candidat][0])
                dw, dh = img.size
                img.close()
                dw, dh = dw / 100, dh / 100
                self.deco_tiles[biome][candidat][1] = (dw, dh)

            dw, dh = self.deco_tiles[biome][candidat][1]

            arrivee = floor(x + dw), floor(y + dh)

            # Si arrivee hors champ
            if not(0 <= arrivee[0] < self.dim[1] and 0 <= arrivee[1] < self.dim[0]):
                continue
            
            arrivee_tuile = self.grille[arrivee[0]][arrivee[1]]

            # Vérifie chevauchement avec les décos existantes
            overlap = False
            for deco_coords, (deco_path, deco_size) in self.deco.items():
                if deco_coords == (x,y):
                    continue
                dx, dy = deco_coords
                dw2, dh2 = deco_size
                # Rectangle de la déco existante
                rect1 = (x, y, x + dw, y + dh)
                rect2 = (dx, dy, dx + dw2, dy + dh2)
                # Test d'intersection
                if not (rect1[2] <= rect2[0] or rect1[0] >= rect2[2] or
                        rect1[3] <= rect2[1] or rect1[1] >= rect2[3]):
                    overlap = True
                    break
            if overlap:
                continue

            # on check la validité de source
            if not tuile_source in ['PPPP', 'SSSS']:
                # alors bbox, donc check validité
                local_x = x - source[0]
                local_y = y - source[1]
                if not test_rectangle(tuile_source, (local_x, local_y), (local_x + dw, local_y + dh)):
                    continue


            if arrivee == source:
                deco_ok.append(candidat)

            # si la deco est à cheval
            else:
                if arrivee_tuile is None:
                    continue
                # On teste biome valide dans l'arrivée
                if biome == 'mer':
                    if arrivee_tuile != 'SSSS':
                        continue
                elif biome == 'terre':
                    if 'P' not in arrivee_tuile:
                        continue
                # On teste position valide
                delta_dw, delta_dh = dw - abs(arrivee[0] - 1), dh - abs(arrivee[1] - 1)
                if test_rectangle(arrivee_tuile, (0,0), (delta_dw, delta_dh)):
                    deco_ok.append(candidat)
        
        return biome, deco_ok
    
    def add_decoration(self, deco:str) -> None:
        """
        Ajoute une décoration à la carte.
        Enregistre dans `self.deco`
        et `self.tiles_to_deco` pour supprimer les decorations lors de la suppression des tiles associés.

        Args:
            deco: Nom de la décoration à ajouter. (contient aussi les coords)
        """
        deco, coords = deco.split('|')
        coords = tuple(map(float, coords.split('*')))

        source = (floor(coords[0]), floor(coords[1]))
        tile_source = self.grille[source[0]][source[1]]
        if 'P' in tile_source:
            biome = 'terre'
        else:
            biome = 'mer'

        path, ims = self.deco_tiles[biome][deco]

        self.deco[coords] = [path, ims]

        if source not in self.tiles_to_deco:
            self.tiles_to_deco[source] = []
        self.tiles_to_deco[source].append(coords)

        arrive = floor(coords[0] + ims[0]), floor(coords[1] + ims[1])

        if arrive != source:
            if arrive not in self.tiles_to_deco:
                self.tiles_to_deco[arrive] = []
            self.tiles_to_deco[arrive].append(coords)









        



    


if __name__ == '__main__':
    map = Map([
        ['RRRP', 'RRPP'],
        ['PPRR', 'RPPR'],
    ])
