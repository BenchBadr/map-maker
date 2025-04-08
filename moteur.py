import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
from deps.map import Map
import deps.ui as ui

addons.init(fltk)
import os

def mainloop():
    #Variables à définir
    global w, h
    w = 600
    h = 600
    end = False

    
    fltk.cree_fenetre(w, h, redimension=True)
    map = Map()
    map.dump_img()

    def draw():
        h, w = fltk.hauteur_fenetre(), fltk.largeur_fenetre()
        # map 
        fltk.image(w//2, h//2, 'deps/map.png', ancrage='center', hauteur=h, largeur=w, tag='map')

        # popup
        ui.create_popup(['popup', True], "Image loaded successfully!")

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
            fltk.efface_tout()
            draw()


        elif ev[0] == 'Redimension':
            fltk.efface_tout()
            draw()



mainloop()