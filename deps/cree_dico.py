import os

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
        tuile[:-4]:path+'/'+tuile 
        for tuile in tuiles
    }

if __name__ == '__main__':
    print(cree_dico('tuiles'))