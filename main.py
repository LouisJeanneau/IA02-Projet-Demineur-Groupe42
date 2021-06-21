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
        commande cmd : .\serveur\win64\crocomine-lite-beta4.exe :8000 .\serveur\grilles\
        ./serveur/win64/crocomine-lite-beta4.exe :8000 ./serveur/grilles/

'''
import os
from client.crocomine_client import CrocomineClient
from typing import List, Tuple
import subprocess
from itertools import combinations

voisins = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
corres = ["T", "S", "C", "N"]

''' FONCTION IMPORTE DEPUIS LE TP SUDOKU ET CREEE '''


# Prend une str pour l'écrire dans le fichier
def write_dimacs_file(dimacs: str, filename: str):
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


# Rajoute une str à la fin du fichier
def append_dimacs_file(dimacs: str, filename: str):
    with open(filename, "a", newline="") as cnf:
        cnf.write(dimacs)


# Supprime la derniere ligne du fichier
def truncate_dimacs_file(filename: str):
    position = 0
    with open(filename) as cnf:
        cnf.seek(0, os.SEEK_END)
        position = cnf.tell()
        position -= 1
        c = ''
        while position != 0 and c != '\n':
            position -= 1
            cnf.seek(position)
            c = cnf.read(1)
            # print(f'voici c : {c}')

    with open(filename, "a", newline="") as cnf:
        cnf.truncate(position + 1)
    return


# Exec le solveur SAT sur le fichier
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


# prend une list de list avec les clauses, et le nb de variables du SAT, pour coder la str CNFmypy
def clauses_to_dimacs(clauses: List[List[int]], nb_vars: int):
    res: str = ""
    res += "p cnf " + str(nb_vars) + " " + str(len(clauses)) + "\n"
    for clause in clauses:
        for literal in clause:
            res += str(literal) + " "
        res += "0\n"
    return res


# FONCTION MAISON POUR CODER LE SAT
def cellToVariable(i: int, j: int, n: int, animal: str) -> int:
    return i * n * 4 + j * 4 + corres.index(animal) + 1


def variableToCell(n: int, var: int) -> Tuple[Tuple[int, int], str]:
    v = var - 1
    return (v // (4 * n), v // 4), corres[v % 4]


def unique(variables: List[int]) -> List[List[int]]:
    return [variables[:]] + [list(a) for a in combinations([-x for x in variables], 2)]


def exactlyOutOf(variables: List[int], k: int) -> List[List[int]]:
    if k == 0:
        return [list(a) for a in combinations([-x for x in variables], 1)]
    if k == len(variables):
        return [list(a) for a in combinations(variables, 1)]
    res: List[List[int]] = [[0]]
    res.pop()
    res.extend([list(a) for a in combinations(variables, len(variables) + 1 - k)])
    res.extend([list(a) for a in combinations([-x for x in variables], k + 1)])
    return res


def getNeighbours(i: int, j: int) -> List[Tuple[int, int]]:
    res: List[Tuple[int, int]] = [(0, 0)]
    res.pop()
    for (k, l) in voisins:
        if 0 <= i + k < m:
            if 0 <= j + l < n:
                res.append(((i + k), (j + l)))
    return res


def codeNeighboursConstraint(neighbours: List[Tuple[int, int]], k: int, animal: str) -> List[List[int]]:
    var: List[int] = []
    for (i, j) in neighbours:
        var.append(cellToVariable(i, j, n, animal))
    return exactlyOutOf(var, k)


def codeFieldConstraint(i, j, field: str) -> List[List[int]]:
    if field == "sea":
        return [[-cellToVariable(i, j, n, "T")]]
    if field == "land":
        return [[-cellToVariable(i, j, n, "S")]]
    return []


def createGridConstraint(m: int, n: int) -> List[List[int]]:
    res: List[List[int]] = [[]]
    res.pop()
    for i in range(m):
        for j in range(n):
            res.extend(unique([cellToVariable(i, j, n, s) for s in corres]))
    return res


def processingInfos(infos, mat, borderQueue: List[Tuple[int, int]]) -> List[List[int]]:
    res: List[List[int]] = []
    if not infos:
        return res
    for info in infos:
        i = info["pos"][0]
        j = info["pos"][1]
        mat[i][j]["isFieldKnown"] = True
        mat[i][j]["fieldType"] = info["field"]
        res.extend(codeFieldConstraint(i, j, info["field"]))
        if "prox_count" in info:
            mat[i][j]["hasBeenCleared"] = True
            mat[i][j]["content"] = "safe"
            mat[i][j]["proxCount"] = info["prox_count"]
            neighbours = getNeighbours(i, j)
            mat[i][j]["isBorder"] = False
            res.append([cellToVariable(i, j, n, "N")])
            for a in range(3):
                res.extend(codeNeighboursConstraint(neighbours, info["prox_count"][a], corres[a]))
            res.extend(codeNeighboursConstraint(neighbours, len(neighbours) - sum(info["prox_count"]), "N"))
            if sum(info["prox_count"]) == 0:
                for neighbour in neighbours:
                    if neighbour in borderQueue:
                        borderQueue.remove(neighbour)
        elif "animal" in info:
            mat[i][j]["hasBeenCleared"] = True
            mat[i][j]["content"] = info["animal"]
            res.append([cellToVariable(i, j, n, info["animal"])])
        else:
            mat[i][j]["isBorder"] = True
            if borderQueue.count((i, j)) == 0:
                borderQueue.append((i, j))
    return res


def makeHypothesis(i: int, j: int) -> Tuple[int, str]:
    for animal in corres:
        append_dimacs_file(str(-cellToVariable(i, j, n, animal)) + " 0\n", "test.cnf")
        solver, trash = exec_gophersat("test.cnf")
        # print(f'resultat du solver sur i={i} j={j} avec animal {animal} :   {solver}')
        if solver:
            truncate_dimacs_file("test.cnf")
        else:
            return True, animal
    return False, "next"


# Fonction de debug
def affichageMat(gridInfos, matInfo):
    print("Affichage de l'état des choses")
    for i in range(gridInfos["m"]):
        for j in range(gridInfos["n"]):
            if matInfo[i][j]["hasBeenCleared"]:
                if matInfo[i][j]["content"] == "safe":
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
def a_game(c: CrocomineClient):
    # on demande la nouvelle carte
    status, msg, gridInfos = c.new_grid()
    global m
    if "m" not in gridInfos:
        print(f'err: no map')
        return
    m = gridInfos["m"]
    global n
    n = gridInfos["n"]

    # Si il y a erreur, on quitte
    if status == "Err":
        print(f'erreur : {msg}')
        return

    # On crée une liste dynamique des clauses
    clause: List[List[int]] = []
    clause.extend(createGridConstraint(m, n))

    # On crée une liste de case en bordure de la zone connue
    borderQueue: List[Tuple[int, int]] = []

    # on crée un modèle de données et rentre les infos dedans
    matInfo = [[{"isFieldKnown": False,
                 "fieldType": "unknown",
                 "hasBeenCleared": False,
                 "content": "unknown",
                 "isBorder": False,
                 "proxCount": (-1, -1, -1),
                 "clearedProx": (0, 0, 0)}
                for j in range(gridInfos["n"])]
               for i in
               range(gridInfos["m"])]

    # On fait un premier discover sur la case de départ
    status, msg, infos = c.discover(gridInfos["start"][0], gridInfos["start"][1])
    # print(status, msg)
    # pprint(infos)
    # affichageMat(gridInfos, matInfo)
    # pprint(clause)

    # On lance la boucle des tours
    while status != "KO" and status != "GG":
        clause.extend(processingInfos(infos, matInfo, borderQueue))
        write_dimacs_file(clauses_to_dimacs(clause, n * m * 4), "test.cnf")
        moveReady = False
        # print(borderQueue)
        while not moveReady:
            border = borderQueue.pop(0)
            moveReady, guess = makeHypothesis(border[0], border[1])
            if moveReady:
                if guess == "N":
                    status, msg, infos = c.discover(border[0], border[1])
                else:
                    status, msg, infos = c.guess(border[0], border[1], guess)
            else:
                borderQueue.append(border)
    return


# fonction qui se lance à l'éxecution
if __name__ == '__main__':
    server = "http://localhost:8000"
    group = "Groupe 42"
    members = "Styvain et Blouis"
    croco = CrocomineClient(server, group, members)
    a_game(croco)
