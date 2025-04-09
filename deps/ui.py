import deps.modules.fltk as fltk
import deps.modules.fltk_addons as addons
addons.init(fltk)


# États des components : visibles ou invisibles
states = {

}

def change_state(key:str) -> None:
    """
    Change l'état d'un component (visible/invisible).

    Args:
        key (str): Identifiant unique du component.
        state (bool): État à appliquer (True pour visible, False pour invisible).

    Returns:
        None
    """
    states[key] = not states[key]

def get_state(key:str) -> bool:
    """
    Récupère l'état d'un component.

    Args:
        key (str): Identifiant unique du component.

    Returns:
        bool: État du component (True pour visible, False pour invisible).
    """
    return states.get(key, False)


def close_active() -> None:
    """
    Ferme tous les popup actifs.
    """
    for key, value in states.items():
        if value:
            states[key] = False

def none_active() -> bool:
    """
    Vérifie si un popup est actif.

    Returns:
        bool: True si un popup est actif, sinon False.
    """
    for key, value in states.items():
        if value:
            return False
    return True


def create_popup(key:list[str, bool], message:str, width=0.8, height=0.8, bg_color="#1e1e1e", color="#b8b8b6") -> None:
    """
    Crée un popup avec un message et un bouton de fermeture. 

    Args:
        key (list[str, bool]): Identifiant unique du popup. Nécessaire pour le fermer.
        message (str): Message du popup
        width (int): largeur du popup.
        height (int): hauteur du popup.
        bg_color (str): Couleur du background du popup.
        color (str): Couleur du texte.

    Returns:
        None: Displays the popup and waits for the user to close it.
    """
    l, w = fltk.hauteur_fenetre(), fltk.largeur_fenetre()
    if key[0] not in states:
        states[key[0]] = key[1]

    if not states[key[0]]:
        return
    
    width, height = width * w, height * l
    c = abs(width - w)//2, abs(height - l)//2

    # fltk.rectangle(c[0], c[1], c[0]+width, c[1]+height, remplissage='yellow', epaisseur=0, tag=key[0])

    # Border radius
    toolbar_color = '#3c3c3c'
    r =  min(min(height*.1, width*.1), 40)
    rc = r // 2

    # toolbar left corner
    fltk.cercle(c[0]+rc, c[1]+rc, rc, remplissage=toolbar_color, epaisseur=0,
                tag=key[0])
    
    # toolbar right corner
    fltk.cercle(c[0]+width - rc, c[1] + rc, rc, remplissage=toolbar_color, epaisseur=0,
                tag=key[0])
    

    # left border
    fltk.rectangle(c[0], c[1]+rc, c[0]+r, c[1]+(height-rc), remplissage=bg_color, epaisseur=0,
                   tag=key[0])


    # bottom left corner
    fltk.cercle(c[0]+rc, c[1]+height - rc, rc, remplissage=bg_color, epaisseur=0,
                tag=key[0])
    
    # bottom border
    fltk.rectangle(c[0]+rc, c[1]+(height - r), c[0]+(width - rc), c[1]+height, remplissage=bg_color, epaisseur=0,
                   tag=key[0])

    
    # bottom right corner
    fltk.cercle(c[0] + width - rc, c[1] + height - rc, rc, remplissage=bg_color, epaisseur=0,
                tag=key[0])
    
    # left vertical border
    fltk.rectangle(c[0]+(width - r), c[1]+rc, c[0]+width, c[1]+(height - rc), remplissage=bg_color, epaisseur=0,
                   tag=key[0])
    
    # Toolbar
    fltk.rectangle(c[0]+rc, c[1], c[0]+(width - rc), c[1]+r, remplissage=toolbar_color, epaisseur=0,
                   tag=key[0])
    
    # Complementary toolbar bottom half
    fltk.rectangle(c[0], c[1]+rc, c[0]+width, c[1]+r, remplissage=toolbar_color, epaisseur=0,
                   tag=key[0])


    # Title 
    fltk.texte(c[0] + width // 2, c[1] + r // 2, message, couleur=color, 
               police='Helvetica bold',
               ancrage="center", taille=int(r // 4), tag=key[0])

    # main area
    fltk.rectangle(c[0]+r, c[1]+r, c[0]+(width - r), c[1]+(height - r), remplissage=bg_color, epaisseur=0, tag=key[0])

    # Close button
    button_size = r // 4
    button_x, button_y = c[0] + button_size * 2 , c[1] + button_size * 2

    # Close button circle
    fltk.cercle(button_x,
                button_y, 
                button_size,
                remplissage="#ec6a5e", tag=f"close_{key[0]}", epaisseur=0)
    
    line_length = button_size // 2


    # Close X (perpendicular lines)
    fltk.ligne(button_x - line_length, 
               button_y - line_length, 
               button_x + line_length, 
               button_y + line_length, couleur="#ec6a5e", tag=f"xclose_{key[0]}", epaisseur=2)
    
    fltk.ligne(button_x - line_length, 
               button_y + line_length, 
               button_x + line_length, 
               button_y - line_length, couleur="#ec6a5e", tag=f"xclose_{key[0]}", epaisseur=2)
    
   
    # Reduce blank
    fltk.cercle(button_x + button_size * 3,
                button_y, 
                button_size,
                remplissage="#5e5f60", epaisseur=0)
    

    # Expand circle
    fltk.cercle(button_x + button_size * 6,
                button_y, 
                button_size,
                remplissage="#61c554", tag=f"expand_{key[0]}", epaisseur=0)
    
    p = button_size*.5

    fltk.rectangle(button_x + button_size * 5 + p,
                   button_y - button_size + p,
                   button_x + button_size * 7 - p,
                   button_y + button_size - p,
                   remplissage='#61c554', epaisseur=0, tag=f'xexpand_{key[0]}')

    
    fltk.ligne(button_x + button_size * 5 + p,
               button_y + button_size - p,
               button_x + button_size * 7 - p,
               button_y - button_size + p,
               couleur='#61c554', epaisseur=2)


def grid_selectors(dim: list[int, int]) -> None:
    """
    Crée une grille sur la fenêtre.
    Cette grille est invisible et permet seulement de traiter les slicks sur les cases.

    Args:
        dim (list[int, int]): Dimensions de la grille.
        color (str): Couleur de la grille.

    Returns:
        None
    """
    w, h = fltk.largeur_fenetre(), fltk.hauteur_fenetre()
    size = min(w, h)
    unit = size // max(dim)

    grid_width = dim[0] * unit
    grid_height = dim[1] * unit

    base_x = (w - grid_width) // 2
    base_y = (h - grid_height) // 2

    for i in range(dim[1]):
        for j in range(dim[0]):
                fltk.rectangle(base_x + j * unit, 
                               base_y + i * unit, 
                               base_x + (j + 1) * unit, 
                               base_y + (i + 1) * unit, 
                               epaisseur=1, 
                               remplissage='white',
                               tag=f"grid_{i}-{j}")
                
def grid(dim: list[int, int], color: str = 'blue') -> None:
    """
    Crée une grille sur la fenêtre.
    Celle-ci est visible.

    Args:
        dim (list[int, int]): Dimensions de la grille.
        color (str): Couleur de la grille.

    Returns:
        None
    """
    w, h = fltk.largeur_fenetre(), fltk.hauteur_fenetre()
    size = min(w, h)
    unit = size // max(dim)

    grid_width = dim[0] * unit
    grid_height = dim[1] * unit

    base_x = (w - grid_width) // 2
    base_y = (h - grid_height) // 2

    # now use fltk.ligne
    for i in range(dim[1] + 1):
        fltk.ligne(base_x, base_y + i * unit, base_x + grid_width, base_y + i * unit, couleur=color)
    for j in range(dim[0] + 1):
        fltk.ligne(base_x + j * unit, base_y, base_x + j * unit, base_y + grid_height, couleur=color)

def draw_hovered(i,j, dim, color='red') -> None:
    """
    Dessine un carré de couleur différente sur la case (i,j) si survolée.
    """
    w, h = fltk.largeur_fenetre(), fltk.hauteur_fenetre()
    size = min(w, h)
    unit = size // max(dim)

    grid_width = dim[0] * unit
    grid_height = dim[1] * unit

    base_x = (w - grid_width) // 2
    base_y = (h - grid_height) // 2

    # now use fltk.ligne
    fltk.rectangle(base_x + j * unit, base_y + i * unit, base_x + (j + 1) * unit, base_y + (i + 1) * unit, couleur=color, tag='grid_hover')