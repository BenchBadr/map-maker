# Compte-rendu


## Tâche 1 - Création du dictionnaire


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