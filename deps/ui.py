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


def create_popup(key:list[str, bool], message:str, width=0.8, height=0.8, bg_color="black", color="white") -> None:
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

    # fltk.rectangle(c[0], c[1], c[0]+width, c[1]+height, remplissage='yellow', epaisseur=0)
    

    # Border radius
    toolbar_color = '#3c3c3c'
    r = min(height*.1, width*.1)

    fltk.cercle(c[0]+r, c[1]+r, r, remplissage=toolbar_color, epaisseur=0)
    fltk.rectangle(c[0], c[1]+r, c[0]+r, c[1]+(height-r), remplissage=bg_color, epaisseur=0)

    fltk.cercle(c[0]+r, c[1]+height - r, r, remplissage=bg_color, epaisseur=0)
    fltk.rectangle(c[0]+r, c[1]+(height - r), c[0]+(width - r), c[1]+height, remplissage=bg_color, epaisseur=0)

    fltk.cercle(c[0]+width - r, c[1] + r, r, remplissage=toolbar_color, epaisseur=0)
    fltk.rectangle(c[0]+r, c[1], c[0]+(width - r), c[1]+r, remplissage=toolbar_color, epaisseur=0)

    fltk.cercle(c[0] + width - r, c[1] + height - r, r, remplissage=bg_color, epaisseur=0)
    fltk.rectangle(c[0]+(width - r), c[1]+r, c[0]+width, c[1]+(height - r), remplissage=bg_color, epaisseur=0)

    # Title 
    fltk.texte(c[0] + width // 2, c[1] + r // 2, message, couleur=color, ancrage="center", taille=int(r // 4))

    # main area
    fltk.rectangle(c[0]+r, c[1]+r, c[0]+(width - r), c[1]+(height - r), remplissage=bg_color, epaisseur=0)

    # Close button
    button_x, button_y = c[0] + width, c[1]
    button_size = r // 4
    fltk.cercle(button_x - button_size * 3,
                button_y + button_size * 2, 
                button_size,
                remplissage="#ec6a5e", tag=f"close_{key[0]}", epaisseur=0)
