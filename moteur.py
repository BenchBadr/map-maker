import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
from deps.map import Map
import deps.ui as ui
addons.init(fltk)

def mainloop():
    #Variables à définir
    global w, h, hovered
    w = 600
    h = 600
    end = False
    grid = True

    selected_tile = None
    global tile_memo
    tile_memo = set()

    map = Map([['MRPM' for _ in range(5)] for i in range(5)])
    map.dump_img()
    
    fltk.cree_fenetre(w, h, redimension=True)

    def draw_popup(key:str) -> None:
        if key == 'popup':
            ui.create_popup(['popup', False], 
                            "Tile Picker", 
                            map.tuiles_selector,
                            args_func={'tile':selected_tile, 'tile_memo':tile_memo},
                            max_width=500, max_height=500)

    def draw():
        h, w = fltk.hauteur_fenetre(), fltk.largeur_fenetre()
        dim = map.dim
        size = min(w, h)
        unit = size//max(dim)
        # window background
        fltk.rectangle(0, 0, w, h, remplissage="grey")
        # grid
        ui.grid_selectors(dim)

        # map 
        map.display_map(unit, (w)//2, (h)//2)
        # fltk.image(w//2, h//2, 'map.png', ancrage='center', hauteur=unit*dim[1], largeur=unit*dim[0])
        if grid:
            ui.grid(dim)

        # selected tile
        if selected_tile != None:
            ui.draw_hovered(selected_tile[0], selected_tile[1], map.dim, color='green')
        # popup
        draw_popup('popup')

    draw()

    hover_effect = []
    dragging = False
    dragged_object = None
    last_x, last_y = None, None

    def erase_popup(key):
        global tile_memo
        for p in ['', 'close_','drag_','expand_','xclose_','xexpand_','blank_']:
            fltk.efface(p+key)
            for tile in tile_memo:
                fltk.efface('tile_'+tile)
            tile_memo = set()


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
            # If dragging, update the position of the dragged object
            if dragging:
                x, y = fltk.abscisse_souris(), fltk.ordonnee_souris()
                if last_x != None:
                    ui.set_coords(dragged_object, x - last_x, y - last_y)
                    erase_popup(dragged_object)
                    draw_popup('popup')
            continue
        elif ev[0] =="Quitte":
            fltk.ferme_fenetre()
            end = True
            break
        elif ev[0] == 'LacheGauche':
            if dragging:
                dragged_object = None
                dragging = False
                # last_x, last_y = None, None
        elif ev[0] == "ClicGauche":
            clicked = set(hovered)
            x, y = fltk.abscisse(ev), fltk.ordonnee(ev)
            for tag in clicked:
                keys = tag.split('_')

                if keys[0] == 'drag' and f'expand_{keys[1]}' not in clicked and f'close_{keys[1]}' not in clicked:
                    if not dragging:
                        dragging = True
                        dragged_object = keys[1]
                        if last_x == None:
                            last_x, last_y = x, y
                if keys[0] == 'close':
                    ui.change_state(keys[1])
                    selected_tile = None
                if keys[0] == 'expand':
                    ui.set_fullscreen(keys[1])
                if keys[0] == 'tile':
                    map.edit_tile(selected_tile[1], selected_tile[0], keys[1])
                    # ui.change_state('popup')
                if len(clicked) == 1:
                    if keys[0] == 'grid' and not dragging:
                        if ui.none_active():
                            tuile = [int(n) for n in tag.split('_')[1].split('-')]
                            # map.edit_tile(tuile[1], tuile[0], 'SSDH')
                            selected_tile = tuile
                            ui.change_state('popup')
            fltk.efface_tout()
            draw()

        elif ev[0] == 'Touche':
            touche = fltk.touche(ev)
            if touche == 'Down' or touche == 'Up':
                if touche == 'Down':
                    map.current_page += 1
                else:
                    map.current_page -= 1
                erase_popup('popup')
                draw_popup('popup')

        elif ev[0] == 'Redimension':
            fltk.efface_tout()
            dragged_object = None
            dragging = False
            last_x, last_y = None, None
            draw()


if __name__ == '__main__':
    mainloop()

# TODO : FIX DRAG AND DROP FULLSCREEN
