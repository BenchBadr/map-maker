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
    def __init__(self, grille=None):
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

    def dump_img(self) -> PIL.Image:
        """
        Renvoie une image représentant la carte.
        Prend soin de ne pas la recréer s'il  suffit de faire des modifications.
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
        self.grille[i][j] = tuile
        self.dump_img()

    def display_map(self, unit, c0, c1, zoom = 1) -> None:
        unit = unit * zoom
        c0 = floor(c0 - (unit*self.dim[0]) // 2 +unit // 2)
        c1 = floor(c1 - (unit*self.dim[1]) // 2 + unit // 2)
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if self.grille[i][j] is not None:
                    fltk.image(c0+i*unit, 
                            c1+j*unit, 
                            self.tuiles[self.grille[i][j]], 
                            hauteur=floor(unit), 
                            largeur=floor(unit))
                else:
                    fltk.rectangle(c0+(i-1/2)*unit, 
                            c1+(j - 1/2)*unit, 
                            c0+(i + 1/2)*unit, 
                            c1+(j + 1/2)*unit, 
                            remplissage='grey',
                            epaisseur=1)
    
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

        neigh = [[key, value] for key, value in self.tuiles.items() if key != tile]
        # neigh = [[t, self.tuiles[t]] for t in tuiles_possibles(self.grille, tile[0], tile[1], self.tuiles)]
        s = len(neigh)
        w, h = abs(x - x2), abs(y - y2)
        unit = min(w, h) // 10
        p = unit // 2

        n_x = floor((w + p) // (unit + p))
        n_y = floor((h + p) // (unit + p))

        pages = ceil(s / (n_x * n_y))
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
