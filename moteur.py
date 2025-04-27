import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
from deps.map import Map
import deps.ui as ui
import deps.save_manager as save
from deps.solver import Solver
addons.init(fltk)
from math import floor, ceil
import sys
sys.setrecursionlimit(10000)  # pour des grilles très grandes

def mainloop():
    #Variables à définir
    global w, h, hovered
    w = 600
    h = 600
    end = False
    grid = True

    zoom = 1

    MAX_ZOOM = 4
    MIN_ZOOM = 0.1
    ZOOM_STEP = 0.1

    deplacement_map = (0,0)
    delta_dep_map = None

    selected_tile = None
    global tile_memo
    tile_memo = set()

    memo_coords = (0,0)

    current_page = 0
    open_mode = True

    game_mode = False

    map = Map()
    solver = Solver(map)

    redim_game = (0,0)

    # Appuyer sur `Escape` pour toggle le mode debug
    map.debug = False
    # Toggle les rivières naturelles si True
    # /!\ Gourmand en ressources, risques de ralentissements.
    map.riviere = True

    state_on_click = 1 # pour eviter erreurs de calculs pour deco

    
    fltk.cree_fenetre(w, h, redimension=True)

    def draw_popup(key:str) -> None:
        '''
        Dessine des popup en fonction de leur clé.
        Couplée à la fonction erase_popup, ces deux fonctions permettent 
        de faire apparaître et disparaître des fenêtres (notamment pour les déplacer)
        sans redessiner le reste.
        '''
        if key == 'popup':
            ui.create_popup(['popup', False], 
                            "Tile Picker", 
                            map.tuiles_selector,
                            args_func={'tile':selected_tile, 'tile_memo':tile_memo},
                            max_width=500, max_height=500)
        if key == 'saved':
            ui.create_popup(['saved', False], 
                            "Save manager",
                            save.file_selector,
                            args_func={'current_page':current_page, 'open_mode': open_mode},
                            width=.8, height=.8)
        if key == 'deco':
            ui.create_popup(['deco', False], 
                            "Decoration Picker", 
                            map.deco_selector,
                            args_func={'tile':selected_tile, 'coords':memo_coords, 'state':state_on_click},
                            max_width=500, max_height=500)
        if key == 'solverr':
            ui.create_popup(['solverr', False], 
                            "Solver Error", content=['Pas de solution trouvée', 'La configuration donnée est impossible'],
                            max_width=500, max_height=500)
    def draw():
        h, w = fltk.hauteur_fenetre(), fltk.largeur_fenetre()
        dim = map.dim
        size = min(w, h)
        unit = size//max(dim)

        # window background
        fltk.rectangle(0, 0, w, h, remplissage="black")
        # grid
        ui.grid_selectors(dim, zoom = zoom, deplacement_map = deplacement_map)

        # map 
        map.display_map(unit, (w)//2, (h)//2, zoom=zoom, deplacement_map=deplacement_map, no_base=game_mode)
        
        # voyant riviere en monde debug
        if map.riviere and map.debug:
            fltk.rectangle(0, 0, w, h, couleur="blue", epaisseur=20)

        if not game_mode:
            if grid:
                ui.grid(dim, zoom=zoom)

            # selected tile
            if selected_tile != None:
                ui.draw_hovered(selected_tile[0], selected_tile[1], map.dim, color='green', zoom = zoom, deplacement_map=deplacement_map)
            
        # popup
        draw_popup('popup')
        draw_popup('saved')
        draw_popup('deco')
        draw_popup('solverr')

    draw()

    hover_effect = []
    dragging = False
    dragged_object = None
    last_x, last_y = None, None

    def erase_popup(key):
        '''
        Efface les popup en fonction de leur clé.
        '''
        global tile_memo
        for p in ['', 'close_','drag_','expand_','xclose_','xexpand_','blank_']:
            fltk.efface(p+key)
            for tile in tile_memo:
                fltk.efface('tile_'+tile)
            tile_memo = set()
        if key == 'deco':
            if map.deco_memo != None:
                for deco in map.deco_memo[0][1]:
                    c = map.deco_memo[1]
                    fltk.efface('decor_'+deco+'|'+f"{c[0]}*{c[1]}")
                map.deco_memo = None


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
        if not game_mode:
            if len(hovered) == 1:
                tag = hovered[0]
                if ui.none_active() and tag.startswith('grid_'):
                    fltk.efface('xgrid_hover')
                    tuile = [int(n) for n in tag.split('_')[1].split('*')]
                    ui.draw_hovered(tuile[0], tuile[1], map.dim, zoom = zoom, deplacement_map = deplacement_map)
            elif len(hovered) == 0:
                fltk.efface('xgrid_hover')


        if ev is None:
            # If dragging, update the position of the dragged object
            if dragging:
                x, y = fltk.abscisse_souris(), fltk.ordonnee_souris()
                if last_x != None:
                    ui.set_coords(dragged_object, x - last_x, y - last_y)
                    erase_popup(dragged_object)
                    draw_popup(dragged_object)
            continue
        elif ev[0] =="Quitte":
            fltk.ferme_fenetre()
            end = True
            break
        elif ev[0] == 'LacheGauche':
            if dragging:
                dragged_object = None
                dragging = False
        elif ev[0] == 'ClicDroit':
            clicked = set(hovered)
            x, y = fltk.abscisse(ev), fltk.ordonnee(ev)
            for tag in clicked:
                keys = tag.split('_')
                if game_mode:
                    continue

                if keys[0] == 'grid':
                    tuile = [int(n) for n in tag.split('_')[1].split('*')]
                    tsl = map.edit_tile(tuile[1], tuile[0], None)[1]

                    # reshape tsl
                    solver.transl_visited(tsl)

                    # remove balises deco
                    if tuple(tuile) in solver.visited:
                        solver.visited.remove(tuple(tuile))

                    if zoom < 1:
                        zoom = 1

                    fltk.efface_tout()
                    draw()


        elif ev[0] == "ClicGauche":
            clicked = set(hovered)
            x, y = fltk.abscisse(ev), fltk.ordonnee(ev)

            for tag in clicked:
                if game_mode:
                    continue

                keys = tag.split('_')

                if keys[0] == 'drag' and f'expand_{keys[1]}' not in clicked and f'close_{keys[1]}' not in clicked:
                    if not dragging:
                        dragging = True
                        dragged_object = keys[1]
                        if last_x == None:
                            last_x, last_y = x, y
                if keys[0] == 'close':
                    ui.change_state(keys[1])
                    if keys[1] == 'deco':
                        map.deco_memo = None
                    selected_tile = None
                if keys[0] == 'expand':
                    ui.set_fullscreen(keys[1])
                if keys[0] == 'tile':
                    selected_tile = map.edit_tile(selected_tile[1], selected_tile[0], keys[1])[0]
                    # ui.change_state('popup')
                if keys[0] == 'decor':
                    map.add_decoration('_'.join(keys[1:]))
                if len(clicked) == 1:
                    if keys[0] == 'grid' and not dragging:
                        if ui.none_active():
                            tuile = [int(n) for n in tag.split('_')[1].split('*')]
                            selected_tile = tuile
                            transl = (selected_tile[0] - map.deplacement_map[1], selected_tile[1] - map.deplacement_map[0])
                            if 0 <= transl[0] < map.dim[0] and 0 <= transl[1] < map.dim[1] \
                                and map.grille[transl[1]][transl[0]] != None:
                                memo_coords = (x,y)
                                state_on_click = zoom, map.deplacement_map
                                ui.change_state('deco')
                            else:
                                ui.change_state('popup')
            fltk.efface_tout()
            draw()

        elif ev[0] == 'Touche':
            touche = fltk.touche(ev)

            if not game_mode:
                # Dézoom
                if touche == '-':
                    zoom = max(zoom - ZOOM_STEP, MIN_ZOOM)
                    fltk.efface_tout()
                    draw()


                # Zoom
                elif touche == '+' or touche == '=':
                    zoom = min(zoom + ZOOM_STEP, MAX_ZOOM)
                    fltk.efface_tout()
                    draw()

                # Réinitialise le zoom
                elif touche == '0':

                    # Si non zoomé, retourne à la position initiale
                    # Permet un double clic
                    if zoom == 1:
                        deplacement_map = (0, 0)
                        map.deplacement_map = (0, 0)
                    zoom = 1
                    fltk.efface_tout()
                    draw()

                # Active / Désactive la grille
                elif touche == '1':
                    grid = not grid
                    fltk.efface_tout()
                    draw()

                # Activer debug
                elif touche == 'Escape':
                    map.debug = not map.debug
                    fltk.efface_tout()
                    draw()

                # Toggle riviere naturelle
                elif touche.lower() == 'r':
                    map.riviere = not map.riviere
                    fltk.efface_tout()
                    draw()

            # Déplacements de la carte
            if touche in ['Left', 'Right', 'Up', 'Down']:
                if not ui.get_state('saved'):
                    # Gauche
                    if touche == 'Left':
                        deplacement_map = (deplacement_map[0] + 1, deplacement_map[1])
                    
                    # Droite
                    elif touche == 'Right':
                        deplacement_map = (deplacement_map[0] - 1, deplacement_map[1])
                    
                if ui.none_active():
                    # Haut
                    if touche == 'Up':
                        deplacement_map = (deplacement_map[0], deplacement_map[1] + 1)

                    # Bas
                    if touche == 'Down':
                        deplacement_map = (deplacement_map[0], deplacement_map[1] - 1)

                delta_dep_map = map.deplacement_map
                map.deplacement_map = deplacement_map
                dep_rel = (deplacement_map[0] - delta_dep_map[0], deplacement_map[1] - delta_dep_map[1])
                if selected_tile is not None:
                    # deplacement relatif
                    selected_tile = (selected_tile[0] + dep_rel[1], selected_tile[1] + dep_rel[0])
                
                print(dep_rel)
                if game_mode and False:
                    # TODO : gestion specifique des cases vides

                    di, dj = dep_rel
                    if di < 0:
                        map.edit_tile(map.dim[0] + deplacement_map[0], 0, None)
                    elif di > 0:
                        map.edit_tile(-1 + deplacement_map[0], 0, None)
                    if dj < 0:
                        map.edit_tile(0, map.dim[1] + deplacement_map[1], None)
                    elif dj > 0:
                        map.edit_tile(0, -1 + deplacement_map[1], None)
                    zoom = w / (3 * unit)
                    # solver.solver(map)
                fltk.efface_tout()
                draw()
                    
            if (ui.get_state('popup') or ui.get_state('deco')) and touche == 'Down' or touche == 'Up':
                if touche == 'Down':
                    map.current_page += 1
                else:
                    map.current_page -= 1
                if ui.get_state('popup'):
                    erase_popup('popup')
                    draw_popup('popup')
                else:
                    erase_popup('deco')
                    draw_popup('deco')

            if ui.get_state('saved'):
                if touche in ['Left', 'Right']:
                    if touche == 'Left':
                        current_page -= 1
                    elif touche == 'Right':
                        current_page += 1
                    erase_popup('saved')
                    draw_popup('saved')

                if touche == 'Return':
                    if not open_mode:
                        save.save_map(map, current_page)
                    else:
                        res = save.open_map(current_page)
                        if res:
                            grille, deco, tiles_to_deco = res
                            map = Map(grille, deco, tiles_to_deco)

                            # Garder une consistence de déplacement
                            map.deplacement_map = deplacement_map
                    ui.change_state('saved')
                    fltk.efface_tout()
                    draw()

                if touche == 'BackSpace':
                    save.delete_map(current_page)
                    fltk.efface_tout()
                    draw()

            if ui.none_active():
                if touche == 'space':
                    game_mode = not game_mode

                    if game_mode:
                        # On ajuste la map pour dim divisible 3
                        def adj_3(a):
                            return (3 - a % 3) % 3
                        
                        for _ in range(adj_3(map.dim[0])):
                            map.edit_tile(map.dim[0], 0, None)
                        for _ in range(adj_3(map.dim[1])):
                            map.edit_tile(0, map.dim[1], None)
                        
                        dim = map.dim
                        size = min(w, h)
                        unit = size/max(dim)

                        zoom = w / (3 * unit)

                        # auto-fill after adjust
                        # solver.solver(map)
                        deplacement_map = (0, 0)
                    fltk.efface_tout()
                    draw()

                if not game_mode:
                    # Gestionnaire de sauvegardes
                    if touche.lower() == 's' or touche.lower() == 'o':
                        open_mode = False
                        if touche.lower() == 'o':
                            open_mode = True
                
                        if not ui.get_state('saved'):
                            ui.change_state('saved')
                            draw_popup('saved')

                    # Decor
                    if touche.lower() == 'd':
                        solver.decorate(map, clear=True)
                        fltk.efface_tout()
                        draw()

                    # Redim + (1,1)
                    if touche.lower() == 'e':
                        map.edit_tile(map.dim[0], map.dim[1], None)
                        fltk.efface_tout()
                        draw()

                    # Solver
                    if touche.lower() == 'i':
                        def draw_func():
                            fltk.efface_tout()
                            draw()
                            fltk.mise_a_jour()
                        if not solver.solver(map, draw=draw_func):
                            ui.change_state('solverr')
                            draw_popup('solverr')
                        fltk.efface_tout()
                        draw()



        elif ev[0] == 'Redimension':
            fltk.efface_tout()
            dragged_object = None
            last_x, last_y = None, None
            if ui.get_state('popup'):
                ui.set_coords('popup',0,0)
            draw()


if __name__ == '__main__':
    mainloop()


