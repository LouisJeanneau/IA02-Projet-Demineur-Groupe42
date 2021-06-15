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
Case: {
    "isFieldKnown" : Bool,
    "fieldType" : str,
    "hasBeenSolved" : Bool,
    "content" : str,
    "proxCount" : (int, int, int),
    "clearedProx" : (int, int, int)
}

    path de mon dossier : \Drive\01_UTC\GI02\ProjetIA02
    commande cmd : .\distrib\win64\crocomine-lite-beta3.exe :8000 .\grilles\
'''
from client.crocomine_client import CrocomineClient
from pprint import pprint

def print_hi(name):
    print(f'Hi, {name}')

def processingInfos(infos, mat):
    for info in infos:

    return



# on commence une partie
def a_game():

    # on demande la nouvelle carte
    status, msg, gridInfos = croco.new_grid()

    #Si il y a erreur, on quitte
    if status=="Err":
        print(f'erreur : {msg}')
        return

    # on crée un modèle de données et rentre les infos dedans
    infoMat = [[{"isFieldKnown" : False, "fieldType" : "unknown", "hasBeenSolved" : False, "content" : "unknown", "proxCount" : (0, 0, 0), "clearedProx" : (0, 0, 0)} for j in range(gridInfos["n"])] for i in range(gridInfos["m"])]

    # On fait un premier discover sur la case de départ, et on traite ce discover
    status, msg, infos = croco.discover(gridInfos["start"][0], gridInfos["start"][1])
    print(status, msg)
    pprint(infos)
    processingInfos(infos, infoMat)



    # On lance la boucle des tours
    while(status != "KO" and status != "GG"):
        return


    return

#fonction qui se lance à l'éxecution
if __name__ == '__main__':
    server = "http://localhost:8000"
    group = "Groupe 42"
    members = "Styvain et Blouis"
    global croco
    croco = CrocomineClient(server, group, members)
    print_hi('PyCharm')
    a_game()

