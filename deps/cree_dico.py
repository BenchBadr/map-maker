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

def cree_deco(path:str) -> dict:
    """
    Renvoie un dictionnaire permettant l'accès aux décorations.
    
    Args:
        path (str): le chemin vers le dossier contenant les dossiers de décoration.
    Returns:
        dict: {mer:{serpent:'mer/serpent.png' ...}}
    """
    deco_type = [folder for folder in os.listdir(path) if not folder[0] == '.']
    res = {biome: {} for biome in deco_type}
    for biome in deco_type:
        deco = os.listdir(path + '/' + biome)
        res[biome] = {
            deco[:-4]:[path + '/' + biome + '/' + deco, None]
            for deco in deco
        }
    return res
if __name__ == '__main__':
    # print(cree_dico('deps/assets/tuiles'))
    print(cree_deco('deps/assets/decors'))