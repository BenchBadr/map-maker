tuiles = ('PMMR', 'GRRH', 'RRGB', 'DHGB', 'MMPM', 'PMPP', 'GRPH', 'MMRM', 'PPRR', 'PRMP', 'SHPH', 'RPRP', 'RMMP', 'FPPM', 'DHRR', 'RPGB', 'MMMP', 'PFFP', 'MPFP', 'DSDF', 'FFFF', 'RPMP', 'PPRM', 'MMMF', 'PPMP', 'PBDP', 'PRRR', 'MMPF', 'MMRP', 'PMFF', 'MFMM', 'PPFM', 'FPMM', 'MPPM', 'FMPF', 'PRRP', 'DSDP', 'PBDR', 'DHPR', 'FFFP', 'FFPP', 'MMMR', 'GBSS', 'DHRP', 'FBSB', 'PMPF', 'GRGS', 'FFPM', 'PFFM', 'PPMF', 'RRPR', 'FFMF', 'SHRH', 'MBSB', 'MPPF', 'PPFP', 'FPPP', 'DSDM', 'SHMH', 'PFMM', 'MFPM', 'FPPF', 'SHGS', 'RMPP', 'MFFP', 'GMGS', 'PMPR', 'PMMF', 'GPPH', 'RPMM', 'MPMM', 'RBSB', 'GFGS', 'DSDR', 'GPGS', 'MPPP', 'PPPP', 'MMFF', 'MPRM', 'FFFM', 'MRPP', 'PRPM', 'PBSB', 'FPMP', 'PRGB', 'MPFM', 'MMPR', 'RMMM', 'FMMP', 'SSSS', 'MMFM', 'FPFF', 'MFPP', 'PMFP', 'RPPR', 'FMPP', 'PPPM', 'PFPM', 'GBDH', 'RPPM', 'MPPR', 'MPFF', 'FFPF', 'MMFP', 'RRPP', 'PFFF', 'RBDR', 'DHPP', 'MMPP', 'MRMM', 'RPRR', 'FMMM', 'PPMM', 'PMMM', 'FMMF', 'FMFF', 'MFFF', 'FPMF', 'PPPF', 'RBDP', 'RRRP', 'PFMP', 'MFFM', 'PPFF', 'PPMR', 'PPGB', 'PRMM', 'MPRP', 'SHFH', 'SSDH', 'FFMM', 'PMRP', 'GPRH', 'RRRR', 'PFPP', 'PMMP', 'MRPM', 'PRPR', 'FFMP', 'MMMM', 'DSSB')

def emplacement_valide(grille:list, i:int, j:int, nom_tuile:str):
    """
    Permet de vérifier si un emplacement est valide en fonction de la tuile.

    Args:
        grille : Grille du MapMaker.
        i : Indice i à vérifier.
        j : Indice j à vérifier.
        nom_tuile : Nom de la nouvelle tuile à vérifier.
    Returns:
        bool : True ou False en fonction de si la nouvelle tuile est plaçable ou non.
    """
    # direction de la case suivante ainsi que l'indice de la case à vérifier
    # Exemple : (1, 0, 2, 0) représente la case i + 1, j + 0 et la 3ème lettre de cette tuile
    # et le 0 représente le haut de la nouvelle tuile à placer "nom_tuile".
    cases_adjacentes = ((0, -1, 1, 3), (-1, 0, 2, 0), (0, 1, 3, 1), (1, 0, 0, 2))
    for dx, dy, ind_tuile, ind_nv_tuile in cases_adjacentes:
        # On vérifie si on est pas en dehors de la grille.
        if (0 <= i + dx < len(grille) and 0 <= j + dy < len(grille[0]) and
                grille[i + dx][j + dy] != None and
                grille[i + dx][j + dy][ind_tuile] != nom_tuile[ind_nv_tuile]):
            return False
    return True


def tuiles_possibles(grille:list, i:int, j:int, list_tuiles:list):
    """
    Ajoute les options des tuiles disponibles dans la case en fonction de toutes les tuiles.

    Args:
        grille : Grille du MapMaker.
        i : Indice i à vérifier.
        j : Indice j à vérifier.
        list_tuiles : Liste de toutes les tuiles disponibles.
    Returns:
        options (list) : Liste contenant les tuiles possibles.
    """
    options = []
    for tuile in list_tuiles:
        if emplacement_valide(grille, i, j, tuile):
            options.append(tuile)
    return options


def main():
    # grille de test du fichier donné
    grille = [['SSSS', 'SSSS', 'SSSS', 'SSSS', None],
              ['SSSS', 'SHGS', 'SHRH', 'SHFH', None],
              ['SSSS', None, 'RMPP', 'FMMM', 'PPMM'],
              ['SSSS', 'GRGS', None, None, None],
              [None, None, None, None, None]]
    i = 3
    j = 2
    nom_tuile = 'PMMR'
    print(emplacement_valide(grille, i, j, nom_tuile))
    print(tuiles_possibles(grille, i, j, tuiles))

main()