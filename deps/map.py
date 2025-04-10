import PIL.Image
try:
    from cree_dico import cree_dico
    import modules.fltk as fltk,modules.fltk_addons as addons
except ImportError:
    from deps.cree_dico import cree_dico
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
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

    def display_map(self, unit, c0, c1):
        c0 = c0 - (unit*self.dim[0]) // 2 +unit // 2
        c1 = c1 - (unit*self.dim[1]) // 2 + unit // 2
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                fltk.image(c0+i*unit, 
                           c1+j*unit, 
                           self.tuiles[self.grille[i][j]], 
                           hauteur=unit, 
                           largeur=unit)
    
    def tuiles_selector(self, key, x, y, x2, y2):
        s = 150
        w, h = abs(x - x2), abs(y - y2)
        unit = min(w, h) // 10
        p = unit // 2
        n_x = floor((w + p) // (unit + p))
        n_y = floor((h + p) // (unit + p))
        pages = ceil(s / (n_x * n_y))
        current_page = 2
        count = 1 + (current_page * (n_x * n_y))
        # effctue un changement de variable pour changer de page
        for i in range(n_y):
            for j in range(min(n_x, s - count)):
                c = (x+j*(unit+p), y+(i)*(unit+p)+p)
                fltk.rectangle(c[0], c[1], c[0]+unit,c[1]+unit, tag=key, remplissage='teal', epaisseur=0)
                fltk.texte(c[0], c[1], f"{count}", taille=int(w//h)*15)
                count += 1
