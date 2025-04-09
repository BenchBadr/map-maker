import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
from deps.map import Map
import deps.ui as ui
addons.init(fltk)

def mainloop():
    #Variables à définir
    global w, h, hovered
    w = 600
    h = 600
    dim_min = 400
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
        ui.create_popup(['popup', False], "Tile Picker", max_width=500, max_height=500)

    draw()

    hover_effect = []

    while not end:
        fltk.mise_a_jour()
        ev = fltk.donne_ev()
        objects = addons.liste_objets_survoles()
        hovered = []
        for obj in objects:
            for info in addons.recuperer_tags(obj):
                if info!='current':
                    hovered.append(info)
                    if info.startswith('close_') or info.startswith('expand_'):
                        tag = info.split('_')[1]
                        fltk.modifie('xclose_'+tag, remplissage='#8c1a11')
                        fltk.modifie('xexpand_'+tag, remplissage='#286018')
                        hover_effect.append(info)

        
        for tag in hover_effect:
            if tag not in hovered:
                hover_effect.remove(tag)
                if tag.startswith('close_') or tag.startswith('expand_'):
                    elem = tag.split('_')[1]
                    fltk.modifie('xclose_'+elem, remplissage='#ec6a5e')
                    fltk.modifie('xexpand_'+elem, remplissage='#61c554')
        
        # hover effects
        if len(hovered) == 1:
            tag = hovered[0]
            if ui.none_active() and tag.startswith('grid_'):
                fltk.efface('grid_hover')
                tuile = [int(n) for n in tag.split('_')[1].split('-')]
                ui.draw_hovered(tuile[0], tuile[1], map.dim)
        elif len(hovered) == 0:
            fltk.efface('grid_hover')


        if ev is None: 
            continue
        elif ev[0] =="Quitte":
            fltk.ferme_fenetre()
            end = True
            break

        elif ev[0] == "ClicGauche":
            clicked = hovered
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
            fltk.efface_tout()
            draw()


        elif ev[0] == 'Redimension':
            fltk.efface_tout()
            draw()


if __name__ == '__main__':
    mainloop()