import PIL.Image
try:
    from cree_dico import cree_dico
    import modules.fltk as fltk,modules.fltk_addons as addons
    from tuiles import tuiles_possibles
except ImportError:
    from deps.cree_dico import cree_dico
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
    from deps.tuiles_tester import tuiles_possibles
addons.init(fltk)
from math import floor, ceil

class Map:
    def __init__(self, grille=None) -> None:
        """
        Initialise la carte avec une grille donnée.
        Args:
            grille: La grille représentant la carte.
        """
        if grille is None:
            # Crée une grille vide de 10x10
            self.grille = [[None for _ in range(10)] for _ in range(10)]
        else:
            self.grille = grille
        self.dim = len(self.grille), len(self.grille[0])
        import os
        self.tuiles = cree_dico('deps/tuiles')
        # Pour mémoïser
        self.img = None
        # used for tile picker
        self.current_page = 0
        self.deplacement_map = (0,0)

    def dump_img(self) -> PIL.Image:
        """
        Renvoie une image représentant la carte.
        Prend soin de ne pas la recréer s'il  suffit de faire des modifications.
        Returns:
            image: L'image représentant la carte.
        """
        x,y = len(self.grille), len(self.grille[0])
        if self.img is not None:
            image = self.img.copy()

            # En cas de changement de taille de la grille
            if image.size != (x*32, y*32):
                # Si plus petit, agrandir la taille de l'image
                if image.size[0] < x or image.size[1] < y:
                    new_image = PIL.Image.new('RGB', (x*32, y*32), color=(255, 255, 255))
                    new_image.paste(image, (0, 0))
                    image = new_image
                else:
                    # Si l'image est plus grande, la recadrer
                    image = image.crop((0, 0, x*32, y*32))

            # Mettre à jour uniquement les cases nécessaires
            for i in range(x):
                for j in range(y):
                    tuile = self.grille[i][j]
                    if tuile is not None:
                        image.paste(PIL.Image.open(self.tuiles[tuile]), (i*32, j*32))
                    else:
                        white_square = PIL.Image.new('RGB', (32, 32), color=(255, 255, 255))
                        image.paste(white_square, (i*32, j*32))
            self.img = image
            
        else:
            image = PIL.Image.new('RGB', (x*32, y*32), color=(255, 255, 255))
            for i in range(x):
                for j in range(y):
                    tuile = self.grille[i][j]
                    if tuile is not None:
                        image.paste(PIL.Image.open(self.tuiles[tuile]), (i*32, j*32))
                    else:
                        # Créer une case blanche si la tuile est None
                        white_square = PIL.Image.new('RGB', (32, 32), color=(255, 255, 255))
                        image.paste(white_square, (i*32, j*32))

        self.img = image
        image.save('map.png')
        return image
    
    def edit_tile(self, i:int, j:int, tuile:str) -> None:
        """
        Modifie la tuile à la position (i, j) de la grille.
        Args:
            i: La coordonnée i de la tuile.
            j: La coordonnée j de la tuile.
            tuile: Le nom de la nouvelle tuile.
        """

        # TODO : handle reshaping

        # Ajuster les coordonnés
        i, j = i - self.deplacement_map[0], j - self.deplacement_map[1]
        # Redimension dynamique et invisible, pour "estomper" la finitude temporaire de la carte
        if i < 0:
            self.grille = [[None for _ in range(self.dim[1])] for _ in range(-i)] + self.grille
            i = 0
        elif i >= self.dim[0]:
            self.grille += [[None for _ in range(self.dim[1])] for _ in range(i - self.dim[0] + 1)]
        if j < 0:
            for k in range(len(self.grille)):
                self.grille[k] = [None for _ in range(-j)] + self.grille[k]
            j = 0
        elif j >= self.dim[1]:
            for k in range(len(self.grille)):
                self.grille[k] = self.grille[k] + [None for _ in range(j - self.dim[1] + 1)]
        self.dim = (len(self.grille), len(self.grille[0]))
        self.grille[i][j] = tuile
        self.dump_img()

        return (j + self.deplacement_map[1], i + self.deplacement_map[0])

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
        h = fltk.hauteur_fenetre()
        w = fltk.largeur_fenetre()

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
                else:
                    fltk.rectangle(c0+(i-1/2)*unit, 
                            c1+(j - 1/2)*unit, 
                            c0+(i + 1/2)*unit, 
                            c1+(j + 1/2)*unit, 
                            remplissage='#555', # Change this color to make Map boundaries visible
                            epaisseur=0)
    
    def tuiles_selector(self, key, x, y, x2, y2, args_func:dict) -> None:
        """
        Dessine la grille de sélection des tuiles.

        Args:
            key: La clé de la fenêtre
            (x,y,x2,y2): Les coordonnées de la fenêtre de dessin (du rectangle de la main area)
            args_func: dictionnaire passant les arguments de la fonction, ici, utilisé pour obtenir le tile selectionné
        """
        tile = args_func['tile']
        tile_memo = args_func['tile_memo']

        # Test interface : Display all tiles
        neigh = [[key, value] for key, value in self.tuiles.items() if key != tile]

        # Get possible tiles properly
        # neigh = [[t, self.tuiles[t]] for t in self.tuiles_possibles(tile[0], tile[1])]
        s = len(neigh)
        w, h = abs(x - x2), abs(y - y2)
        unit = min(w, h) // 10
        p = unit // 2

        n_x = floor((w + p) // (unit + p))
        n_y = floor((h + p) // (unit + p))

        pages = ceil(s / (n_x * n_y))

        if pages == 0:
            texte = 'Impossible'
            taille = floor(abs(x - x2) // len(texte))
            fltk.texte(x+taille*2, floor(y + abs(y - y2) / 2 - taille), texte, couleur='#8a4641', taille=taille, tag=key)
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

    def emplacement_valide(self, i:int, j:int, nom_tuile:str) -> bool:
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
        directions = (0,1), (1,0), (0,-1), (-1,0)
        for dr, dc in directions:
            # check boundaries
            if i+dr >= self.dim[0] or i+dr < 0 or j+dc >= self.dim[1] or j + dr < 0:
                continue
            # check if the tile is not None
            if self.grille[i+dr][j+dc] is None:
                continue

            voisin = self.grille[i+dr][j+dc]
            # check if the tile is compatible
            ## vertical check
            if i + dr > i:
                if nom_tuile[0] != self.grille[i+dr][j+dc][2]:
                    return False
            else:
                if nom_tuile[2] != self.grille[i+dr][j+dc][0]:
                    return False
            ## horizontal check
            if j + dc > j:
                if nom_tuile[1] != self.grille[i+dr][j+dc][3]:
                    return False
            else:
                if nom_tuile[3] != self.grille[i+dr][j+dc][1]:
                    return False
                
            if nom_tuile[1] == 'D' and voisin[3] not in ['S']:  # Côte à droite
                return False
        return True
    
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
            if self.emplacement_valide(i, j, tuile):
                options.append(tuile)
        return options
