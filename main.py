'''
types de base :

Status : str
Mgg : str
Info: {
    “pos”: (int, int), # (i, j) i < M, j < N
    “field”: str # “sea”“land”
    “prox_count”: (int, int, int) # (tiger_count, shark_count, croco_count), optional
    }
Infos = List[info]
GridInfos: {
    “m”: int,
    “n”: int,
    “start”: (int, int),
    “tiger_count”: int,
    “shark_count”: int,
    “croco_count”: int,
    “sea_count”: int,
    “land_count”: int,
    “3BV”: int,
    “infos”: Infos # Optional
    }
'''


def print_hi(name):
    print(f'Hi, {name}')

#fonction qui se lance à l'éxecution
if __name__ == '__main__':

    print_hi('PyCharm')

# on commence une partie
def a_game():
    # on demande la nouvelle carte
    status, msg, gridInfos = new_grid()

    # on crée un modèle de données et rentre les infos dedans


    # On fait un premier discover sur la case de départ, et on traite ce discover

    # On lance la boucle des tours
    while(status != "KO" && status != "GG"):

    return