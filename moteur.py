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
    grid = True

    map = Map([['MRPM' for _ in range(10)] for i in range(20)])
    map.dump_img()
    
    fltk.cree_fenetre(w, h, redimension=True)

    def draw():
        h, w = fltk.hauteur_fenetre(), fltk.largeur_fenetre()
        dim = map.dim
        size = min(w, h)
        unit = size//max(dim)
        # window background
        fltk.rectangle(0, 0, w, h, remplissage="white")
        # grid
        ui.grid_selectors(dim)

        # map 
        fltk.image(w//2, h//2, 'map.png', ancrage='center', hauteur=unit*dim[1], largeur=unit*dim[0])
        if grid:
            ui.grid(dim)
        # popup
        ui.create_popup(['popup', False], "Tile Picker")

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
            clicked = []
            for obj in objects:
                for info in addons.recuperer_tags(obj):
                    if info!='current':
                        clicked.append(info)

            print(clicked)
            if len(clicked) == 0:
                ui.close_active()
            for tag in clicked:
                if tag.startswith('close_'):
                    key = tag.split('_')[1]
                    ui.change_state(key)
                if len(clicked) == 1:
                    if tag.startswith('grid_'):
                        if ui.none_active():
                            tuile = [int(n) for n in tag.split('_')[1].split('-')]
                            map.edit_tile(tuile[1], tuile[0], 'SSDH')
                            ui.change_state('popup')
                        else:
                            ui.close_active()
            fltk.efface_tout()
            draw()


        elif ev[0] == 'Redimension':
            fltk.efface_tout()
            draw()


if __name__ == '__main__':
    mainloop()