---
marp: true
---

# Hello

- hello

---
# Création du dictionnaire


> La première tâche consiste à parcourir les fichiers fournis pour récupérer toutes les tuiles disponibles.
>
> On propose de construire un dictionnaire dont les clefs sont les noms des tuiles (par exemple, `"MMPR"` pour la tuile de la Fig. 5a) et les valeurs associées sont les chemins d’accès relatifs des images des tuiles correspondantes (par exemple, `"tuiles/MMPR.png"`).
>
> **Indication** : la fonction `listdir` du module `os` permet de récupérer une liste de tous les fichiers se trouvant dans un répertoire donné.
>
> Implémentez une fonction `cree_dico(chemin)` qui renvoie ce dictionnaire à partir du chemin d’accès du répertoire contenant les tuiles.

> [!WARNING]
> pour implémenter les niveaux supérieurs de certaines tâches, il pourrait être nécessaire d’enrichir cette structure de données.

```python
def cree_dico(path:str) -> dict:
    """
    Les clefs sont les noms des fichiers sans l'extension et les valeurs sont les chemins vers les fichiers.
    
    Args:
        path (str): le chemin vers le dossier contenant les tuiles
    Returns:
        dict: les clefs sont les noms des tuiles et les valeurs sont les images
    """
    tuiles = os.listdir(path)
    return {
        tuile[:-3]:path+'/'+tuile 
        for tuile in tuiles
    }
```

En premier lieu, on écrie `cree_dico` de la façon suivante.

# Moteur et placement des tuiles

> La deuxième tâche du projet consiste à programmer la logique interne de MapMaker (le moteur),
c’est-à-dire la partie qui permet de représenter l’état de la carte dans des structures de données
appropriées, et de les modifier durant l’utilisation du programme.


## Fenêtre Apple

Fonctionnalités implémentées:
- Drag and drop
- Fullscreen
- Close
Entièrement responsive. 


## Modification `fltk`

Après création de notre fenêtre avec `ui.py`, il est cependant impossible de la déplacer en imitant un comportement de drag, car simplement impossible avec `fltk`. 


La première approche a été de cliquer sur la toolbar supérieure (celle contenant les boutons d'actions fermer / maximiser) puis un deuxième clic permettait d'arrêter le redimensionement. Cependant dû au temps de dessin de la fenêtre, un décalage entre la souris et cette dernière subvenait.

Les déplacements étaient définis avec le vecteur entre les coordonnées actuelles et précédentes de la souris.

Un événement `LacheGauche` a été ceéé, utilisant l'événement `<ButtonRelease-1>`

# Keyboard
- `Up`
    - Déplacement map
    - Scroll dans fenêtre
- `Down`
    - Déplacement map
    - Scroll dans fenêtre
- `Left`
    - Déplacement map
- `Right`
    - Déplacement map
- `0`
    - Réinitialise le zoom
- `-`
    - Zoom - 
- `+`
    - Zoom +
    - If not zoomed, reinitialize position
- `1` 
    - Toggle grid
- `Escape`
    - Toggle debug mode
- `R`
    - Toggle riviere naturelle
- `S`
    - Save file through manager
- `O`
    - Open file through manager
- `Backspace`
    - When in save manager, delete files
- `E`
    - Expand map + (1,1) dim

# Ouverture

Espérance de vie