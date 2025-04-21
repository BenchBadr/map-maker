import time
import base64
import os
import locale
from datetime import datetime
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
import PIL.Image
try:
    import modules.fltk as fltk,modules.fltk_addons as addons
except ImportError:
    import deps.modules.fltk as fltk,deps.modules.fltk_addons as addons
addons.init(fltk)
from math import ceil

def file_selector(key:str, x:int, y:int, x2:int, y2:int, args_func:dict) -> None:
    """
    Ouvre une fenêtre de sélection de fichier et renvoie le chemin du fichier sélectionné.
    """
    fichiers = os.listdir('saves/maps')
    n = len(fichiers)

    open_mode = args_func['open_mode']
    current_page = args_func['current_page'] % (n + 1 if not open_mode else n)

    unit = min(10, (x2 -x) // (4*n + 1))
    length = unit * (4*n)
    p = abs(x2 - x - length) // 2

    c = x + p, y2
    for i in range(n + 1 if not open_mode else n):
        remp = '#58b5ca' if i == current_page else '#3c3c3c'
        fltk.cercle(c[0] + 4 * i * unit, c[1], unit, remplissage=remp, epaisseur=0, tag=key)

    c2 = x, y + unit, x2, y2 - unit * 2
    sub_page = x2 - x, y2 - unit * 2 - y + unit

    a,b,r,rat = c2[0]+sub_page[0]//2, c2[1]+sub_page[1]//2, min(sub_page)//4, .6

    if not open_mode:
        if current_page == 0:
            fltk.cercle(a,b,r, remplissage='#00CBA9', epaisseur=0, tag=key)
            fltk.ligne(a-r*rat, b, a+r*rat, b, epaisseur=unit, tag=key, couleur='#f0eee7')
            fltk.ligne(a, b - r*rat, a, b+r*rat, epaisseur=unit, tag=key, couleur='#f0eee7')

            # adoucir le +
            fltk.cercle(a -r*rat,b,unit//2, remplissage='#f0eee7', epaisseur=0, tag=key)
            fltk.cercle(a + r*rat,b,unit//2, remplissage='#f0eee7', epaisseur=0, tag=key)
            fltk.cercle(a,b + r * rat,unit//2, remplissage='#f0eee7', epaisseur=0, tag=key)
            fltk.cercle(a,b - r * rat,unit//2, remplissage='#f0eee7', epaisseur=0, tag=key)

            # Texte
            t1 = 'Nouveau fichier'
            t2 = 'Appuyez sur Entrée pour créer un nouveau fichier'

            taille1 = int((5*r)//len(t1))
            taille2 = int((5*r)//len(t2))

            fltk.texte(a - taille1*len(t1)*.3, c2[1], t1, couleur='white', tag=key, taille=taille1)
            fltk.texte(a - taille2*len(t2)*.3, c2[1] + taille1 * 2, t2, couleur='#888', tag=key, taille=taille2)
            return


    # Aucun fichier à ouvrir
    if open_mode and n == 0:

        # Texte
        t1 = 'Aucun fichier trouvé'
        t2 = 'Commencez par sauvegarder une carte avant de l\'ouvrir'

        taille1 = int((5*r)//len(t1))
        taille2 = int((5*r)//len(t2))

        fltk.texte(a - taille1*len(t1)*.3, c2[1] + 2*r, t1, couleur='white', tag=key, taille=taille1)
        fltk.texte(a - taille2*len(t2)*.3, c2[1] + 2*r + taille1 * 2, t2, couleur='#888', tag=key, taille=taille2)
        return
    
    idx = current_page if open_mode else current_page - 1
    name = fichiers[idx][:-4]
    timestamp = float(base64.b64decode(name).decode())

    # Texte
    t1 = datetime.fromtimestamp(timestamp).strftime('%A %d %B, à %Hh%M')
    if open_mode:
        t2 = 'Appuyez sur Entrée pour ouvrir le fichier'
    else:
        t2 = 'Appuyez sur Entrée pour remplacer le fichier'

    taille1 = int((5*r)//len(t1))
    taille2 = int((5*r)//len(t2))

    fltk.texte(a - taille1*len(t1)*.3, c2[1], t1, couleur='white', tag=key, taille=taille1)
    fltk.texte(a - taille2*len(t2)*.3, c2[1] + taille1 * 2, t2, couleur='#888', tag=key, taille=taille2)

    fltk.image(a, b,'saves/images/' + name + '.png', tag=key, hauteur=ceil(2*r), largeur=ceil(2*r))
    return


def save_map(map, current_page):
    """
    Sauvegarde la carte dans un fichier.
    """
    current_page = current_page % (len(os.listdir('saves/maps')) + 1)
    if current_page == 0:
        # New file
        name = base64.b64encode(str(time.time()).encode()).decode()
    else:
        name = os.listdir('saves/maps')[current_page - 1][:-4]
        print(current_page, name)
    map.dump_img('saves/images/' + name + '.png')
    save_path = os.path.join('saves', 'maps', f"{name}.map")
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(str(map.grille))
        f.close()

def open_map(map, current_page):
    """
    Ouvre un fichier de carte et charge la carte.
    """
    current_page = current_page % len(os.listdir('saves/maps'))
    name = os.listdir('saves/maps')[current_page ][:-4]
    save_path = os.path.join('saves', 'maps', f"{name}.map")
    with open(save_path, 'r', encoding='utf-8') as f:
        grille = eval(f.read())
        f.close()
    return grille
    
def clear_saves():
    """
    Supprime tous les fichiers de sauvegarde.
    """
    for file in os.listdir('saves/maps'):
        os.remove(os.path.join('saves/maps', file))
    for file in os.listdir('saves/images'):
        os.remove(os.path.join('saves/images', file))
    print('Fichiers de sauvegarde supprimés!')
    return True

if __name__ == '__main__':
    clear_saves()