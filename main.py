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
        commande cmd : .\serveur\win64\crocomine-lite-beta3.exe :8000 .\serveur\grilles\
'''
from client.crocomine_client import CrocomineClient
from pprint import pprint
from typing import List, Tuple
import subprocess
from itertools import combinations


def print_hi(name):
    print(f'Hi, {name}')


# FONCTION IMPORTE DEPUIS LE TP SUDOKU
def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


def exec_gophersat(
        filename: str, cmd: str = "gophersat-1.1.6.exe", encoding: str = "utf8") -> Tuple[bool, List[int]]:
    result = subprocess.run([cmd, filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
                            encoding=encoding)
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:].split(" ")

    return True, [int(x) for x in model]


def clauses_to_dimacs(clauses, nb_vars):
    res: str = ""
    res += "p cnf " + str(nb_vars) + " " + str(len(clauses)) + "\n"
    for clause in clauses:
        for literal in clause:
            res += str(literal) + " "
        res += "0\n"
    return res


def processingInfos(infos, mat):
    if not infos:
        return
    for info in infos:
        i = info["pos"][0]
        j = info["pos"][1]
        mat[i][j]["isFieldKnown"] = True
        mat[i][j]["fieldType"] = info["field"]
        if "prox_count" in info:
            mat[i][j]["hasBeenCleared"] = True
            mat[i][j]["content"] = "safe"
            mat[i][j]["proxCount"] = info["prox_count"]
    return


def affichageMat(gridInfos, matInfo):
    print("Affichage de l'état des choses")
    for i in range(gridInfos["m"]):
        for j in range(gridInfos["n"]):
            if (matInfo[i][j]["hasBeenCleared"]):
                if (matInfo[i][j]["content"] == "safe"):
                    print("O", end=' ')
                else:
                    print(matInfo[i][j]["content"], end=' ')
            elif matInfo[i][j]["isFieldKnown"]:
                if matInfo[i][j]["fieldType"] == "sea":
                    print("~", end=' ')
                else:
                    print("x", end=' ')
            else:
                print("?", end=' ')
        print(" ")
    return


# on commence une partie
def a_game():
    # on demande la nouvelle carte
    status, msg, gridInfos = croco.new_grid()

    # Si il y a erreur, on quitte
    if status == "Err":
        print(f'erreur : {msg}')
        return

    # on crée un modèle de données et rentre les infos dedans
    matInfo = [[{"isFieldKnown": False, "fieldType": "unknown", "hasBeenCleared": False, "content": "unknown",
                 "proxCount": (-1, -1, -1), "clearedProx": (0, 0, 0)} for j in range(gridInfos["n"])] for i in
               range(gridInfos["m"])]

    # On fait un premier discover sur la case de départ, et on traite ce discover
    status, msg, infos = croco.discover(gridInfos["start"][0], gridInfos["start"][1])
    print(status, msg)
    pprint(infos)
    processingInfos(infos, matInfo)
    affichageMat(gridInfos, matInfo)

    # On lance la boucle des tours
    while (status != "KO" and status != "GG"):
        return

    return


# fonction qui se lance à l'éxecution
if __name__ == '__main__':
    server = "http://localhost:8000"
    group = "Groupe 42"
    members = "Styvain et Blouis"
    global croco
    croco = CrocomineClient(server, group, members)
    print_hi('PyCharm')
    a_game()
