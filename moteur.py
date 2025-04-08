import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
from deps.map import Map
import deps.ui as ui
addons.init(fltk)
import asyncio

def mainloop():
    #Variables à définir
    global w, h
    w = 600
    h = 600
    end = False

    map = Map([['MRPM' for _ in range(10)] for i in range(20)])
    map.dump_img()
    
    fltk.cree_fenetre(w, h, redimension=True)

    def draw():
        h, w = fltk.hauteur_fenetre(), fltk.largeur_fenetre()
        dim = map.dim
        size = min(w, h)
        unit = size//max(dim)
        # grid
        ui.grid_selectors(dim)

        # map 
        fltk.image(w//2, h//2, 'map.png', ancrage='center', hauteur=unit*dim[1], largeur=unit*dim[0], tag='map')
        ui.grid(dim)
        # popup
        ui.create_popup(['popup', False], "Tile Picker", bg_color='red')

    draw()

    while not end:
        fltk.mise_a_jour()
        ev = fltk.donne_ev()


        if ev is None: 
            continue
        elif ev[0] =="Quitte":
            fltk.ferme_fenetre()
            end = True
            break

        elif ev[0] == "ClicGauche":

            objects = addons.liste_objets_survoles()

            for obj in objects:
                sommet = [info for info in addons.recuperer_tags(obj) if info != 'current']
                for tag in sommet:
                    if tag.startswith('close_'):
                        key = tag.split('_')[1]
                        ui.change_state(key)
                    if tag.startswith('grid_'):
                        tuile = tag.split('_')[1].split('-')
                        print(tuile)
            fltk.efface_tout()
            draw()


        elif ev[0] == 'Redimension':
            fltk.efface_tout()
            draw()


if __name__ == '__main__':
    mainloop()