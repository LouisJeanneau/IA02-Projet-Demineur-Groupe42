import os
import random

from client.crocomine_client import CrocomineClient
from typing import List, Tuple
import subprocess
from itertools import combinations
import pycryptosat
from helpers.timer import Timer, TimerError
from multiprocessing import Process
import sys

voisins = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
corres = ["T", "S", "C", "N"]

''' FONCTION IMPORTE DEPUIS LE TP SUDOKU ET CREEE '''


# Prend une str pour l'écrire dans le fichier
def write_dimacs_file(dimacs: str, filename: str):
    """
    Ecrit la str dimacs dans le fichier filename
    :param dimacs:
    :param filename:
    :return:
    """
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)


# Rajoute une str à la fin du fichier
def append_dimacs_file(dimacs: str, filename: str):
    with open(filename, "a", newline="") as cnf:
        cnf.write(dimacs)


# Supprime la derniere ligne du fichier
def truncate_dimacs_file(filename: str):
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
def cell_to_variable(i: int, j: int, n: int, animal: str) -> int:
    return i * n * 4 + j * 4 + corres.index(animal) + 1


def variable_to_cell(n: int, var: int) -> Tuple[Tuple[int, int], str]:
    v = var - 1
    return (v // (4 * n), v // 4), corres[v % 4]


def unique(variables: List[int]) -> List[List[int]]:
    return [variables[:]] + [list(a) for a in combinations([-x for x in variables], 2)]


def exactly_out_of(variables: List[int], k: int) -> List[List[int]]:
    if k == 0:
        return [list(a) for a in combinations([-x for x in variables], 1)]
    if k == len(variables):
        return [list(a) for a in combinations(variables, 1)]
    res: List[List[int]] = [[0]]
    res.pop()
    res.extend([list(a) for a in combinations(variables, len(variables) + 1 - k)])
    res.extend([list(a) for a in combinations([-x for x in variables], k + 1)])
    return res


def get_neighbours(i: int, j: int, m: int, n: int) -> List[Tuple[int, int]]:
    res: List[Tuple[int, int]] = [(0, 0)]
    res.pop()
    for (k, l) in voisins:
        if 0 <= i + k < m:
            if 0 <= j + l < n:
                res.append(((i + k), (j + l)))
    return res


def code_neighbours_constraint(neighbours: List[Tuple[int, int]], n: int, k: int, animal: str) -> List[List[int]]:
    var: List[int] = []
    for (i, j) in neighbours:
        var.append(cell_to_variable(i, j, n, animal))
    return exactly_out_of(var, k)


def code_field_constraint(i, j, n: int, field: str) -> List[List[int]]:
    if field == "sea":
        return [[-cell_to_variable(i, j, n, "T")]]
    if field == "land":
        return [[-cell_to_variable(i, j, n, "S")]]
    return []


def create_grid_constraint(m: int, n: int) -> List[List[int]]:
    res: List[List[int]] = []
    for i in range(m):
        for j in range(n):
            res.extend(unique([cell_to_variable(i, j, n, s) for s in corres]))
    return res


def processing_infos(infos, mat, border_queue: List[Tuple[int, int]], discover_queue: List[Tuple[int, int]],
                     chord_queue: List[Tuple[Tuple[int, int], int]]) -> List[List[int]]:
    res: List[List[int]] = []
    if not infos:
        return res

    for info in infos:
        i = info["pos"][0]
        j = info["pos"][1]
        if not "prox_count" in info and not "animal" in info:
            # on precise l'info du type de terrain
            mat[i][j]["isFieldKnown"] = True
            mat[i][j]["fieldType"] = info["field"]
            # on code les contraintes liees au terrain
            res.extend(code_field_constraint(i, j, len(mat[0]), info["field"]))

            mat[i][j]["isBorder"] = True
            if border_queue.count((i, j)) == 0:
                border_queue.append((i, j))
        else:
            # c'est un animal ou une case vide
            mat[i][j]["hasBeenCleared"] = True
            if discover_queue.count((i, j)):
                discover_queue.remove((i, j))

            neighbours = get_neighbours(i, j, len(mat), len(mat[0]))
            for neighbour in neighbours:
                mat[neighbour[0]][neighbour[1]]["cleared_neighbours"] += 1
                if "animal" in info:
                    mat[neighbour[0]][neighbour[1]]["cleared_prox"][corres.index(info["animal"])] += 1
                    if sum(mat[neighbour[0]][neighbour[1]]["prox_count"]) == sum(
                            mat[neighbour[0]][neighbour[1]]["cleared_prox"]) and mat[neighbour[0]][neighbour[1]][
                        "cleared_neighbours"] < mat[neighbour[0]][neighbour[1]]["neighbours"] - 1:
                        mat[neighbour[0]][neighbour[1]]["discovered_border"] = True
                        chord_queue.append(((neighbour[0], neighbour[1]), mat[neighbour[0]][neighbour[1]]["neighbours"] - mat[neighbour[0]][neighbour[1]][
                        "cleared_neighbours"]))
                if mat[neighbour[0]][neighbour[1]]["cleared_neighbours"] == mat[neighbour[0]][neighbour[1]][
                    "neighbours"]:
                    mat[neighbour[0]][neighbour[1]]["discovered_border"] = False

            if "prox_count" in info:
                # c'est une case vide
                mat[i][j]["content"] = "safe"
                mat[i][j]["prox_count"] = list(info["prox_count"])
                mat[i][j]["isBorder"] = False
                res.append([cell_to_variable(i, j, len(mat[0]), "N")])
                for a in range(3):
                    res.extend(code_neighbours_constraint(neighbours, len(mat[0]), info["prox_count"][a], corres[a]))
                res.extend(
                    code_neighbours_constraint(neighbours, len(mat[0]), len(neighbours) - sum(info["prox_count"]), "N"))
                if sum(info["prox_count"]) == 0:
                    for neighbour in neighbours:
                        if neighbour in border_queue:
                            border_queue.remove(neighbour)
                        if neighbour in discover_queue:
                            discover_queue.remove(neighbour)

            elif "animal" in info:
                # la case en question est un animal
                mat[i][j]["cleared_prox"][corres.index(info["animal"])] += 1
                mat[i][j]["content"] = info["animal"]
                res.append([cell_to_variable(i, j, len(mat[0]), info["animal"])])

    return res


def make_hypothesis(i: int, j: int, n: int, s: pycryptosat.Solver) -> Tuple[int, str]:
    for animal in corres:
        # append_dimacs_file(str(-cellToVariable(i, j, n, animal)) + " 0\n", "test.cnf")
        solver, trash = s.solve([-cell_to_variable(i, j, n, animal)])
        # solver, trash = exec_gophersat("test.cnf")
        # print(f'resultat du solver sur i={i} j={j} avec animal {animal} :   {solver}')
        if not solver:
            return True, animal
    return False, "next"


def make_multiple_hypothesis(border_queue: List[Tuple[int, int]], n: int, s: pycryptosat.Solver) -> Tuple[
    List[Tuple[int, int]], List[Tuple[int, int, str]]]:
    resDiscover: List[Tuple[int, int]] = []
    resGuess: List[Tuple[int, int, str]] = []
    for i, j in border_queue:
        found_one, which = make_hypothesis(i, j, n, s)
        if found_one:
            border_queue.remove((i, j))
            if which == "N":
                resDiscover.append((i, j))
            else:
                resGuess.append((i, j, which))
    return resDiscover, resGuess


def create_discovered_border_list(matInfo):
    return


def optimize_discovers(discover_queue: List[Tuple[int, int]], matInfo):
    return


# Fonction de debug
def affichage_mat(gridInfos, matInfo):
    print("Affichage de l'état des choses")
    for i in range(gridInfos["m"]):
        for j in range(gridInfos["n"]):
            if matInfo[i][j]["hasBeenCleared"]:
                if matInfo[i][j]["discovered_border"]:
                    print("•", end=' ')
                elif matInfo[i][j]["content"] == "safe":
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


def affichage_cleared_neighbours(gridInfos, matInfo):
    for i in range(gridInfos["m"]):
        for j in range(gridInfos["n"]):
            print(f'{matInfo[i][j]["cleared_neighbours"]}', end=' ')
        print(" ")
    print("\n\n")


# on commence une partie
def a_game(c: CrocomineClient):
    # on demande la nouvelle carte
    status, msg, gridInfos = c.new_grid()

    # Si il y a erreur, on quitte
    if status == "Err":
        print(f'erreur : {msg}')
        return status, msg

    # sinon on récupère la taille de la map
    m = gridInfos["m"]
    n = gridInfos["n"]

    # On crée une liste dynamique des clauses
    clause: List[List[int]] = []
    clause.extend(create_grid_constraint(m, n))

    s = pycryptosat.Solver()
    s.add_clauses(clause)

    # On crée une liste de case en bordure de la zone connue
    border_queue: List[Tuple[int, int]] = []

    # on crée un modèle de données et rentre les infos dedans
    mat_info = [[{"isFieldKnown": False,
                  "fieldType": "unknown",
                  "hasBeenCleared": False,
                  "content": "unknown",
                  "isBorder": False,
                  "prox_count": [-1, -1, -1],
                  "cleared_prox": [0, 0, 0],
                  "discovered_border": False,
                  "neighbours": 8,
                  "cleared_neighbours": 0}
                 for j in range(gridInfos["n"])]
                for i in
                range(gridInfos["m"])]

    # Alors ici on met a jour le nombre de voisins pour les cases en bordures
    for i in [0, m - 1]:
        for j in range(n):
            mat_info[i][j]["neighbours"] = 5
    for j in [0, n - 1]:
        for i in range(m):
            mat_info[i][j]["neighbours"] = 5
    for i, j in [(0, 0), (0, n - 1), (m - 1, 0), (m - 1, n - 1)]:
        mat_info[i][j]["neighbours"] = 3

    # On fait un premier discover sur la case de départ
    status, msg, infos = c.discover(gridInfos["start"][0], gridInfos["start"][1])

    discover_queue: List[Tuple[int, int]] = []
    guess_queue: List[Tuple[int, int, str]] = []
    chord_queue: List[Tuple[Tuple[int, int], int]] = []

    s.add_clauses(processing_infos(infos, mat_info, border_queue, discover_queue, chord_queue))

    # On lance la boucle des tours
    while status != "KO" and status != "GG":
        discover_queue_temp, guess_queue_temp = make_multiple_hypothesis(border_queue, n, s)
        discover_queue.extend(discover_queue_temp)
        guess_queue.extend(guess_queue_temp)
        print(f"borderQ : {border_queue}\nchordQ : {chord_queue}\ndiscoverQ : {discover_queue}\nguessQ : {guess_queue}\n\n")
        played = False
        if guess_queue:
            played = True
            while guess_queue:
                guess = guess_queue.pop(0)
                status, msg, infos = c.guess(guess[0], guess[1], guess[2])
                if status == "KO":
                    return status, msg
                s.add_clauses(processing_infos(infos, mat_info, border_queue, discover_queue, chord_queue))
        elif chord_queue:
            played = True
            chord_queue.sort(key=lambda ch: ch[1])
            while chord_queue:
                # print(f'chordQ : {chord_queue}')
                chord = chord_queue.pop(0)
                status, msg, infos = c.chord(chord[0][0], chord[0][1])
                if status == "KO":
                    return status, msg
                neighbours = get_neighbours(chord[0][0], chord[0][1], m, n)
                for neighbour in neighbours:
                    if discover_queue.count(neighbour):
                        discover_queue.remove(neighbour)
                    if neighbour in border_queue:
                        border_queue.remove(neighbour)
                s.add_clauses(processing_infos(infos, mat_info, border_queue, discover_queue, chord_queue))
                # print(f'discoverQ dans le chord : {discover_queue}')
        elif discover_queue and not played:
            played = True
            discover = discover_queue.pop(0)
            # print(f' clearedprox : {mat_info[discover[0]][discover[1]]["cleared_prox"]} et proxcount {mat_info[discover[0]][discover[1]]["prox_count"]}')
            status, msg, infos = c.discover(discover[0], discover[1])
            if status == "KO":
                return status, msg
            s.add_clauses(processing_infos(infos, mat_info, border_queue, discover_queue, chord_queue))
        if not played:
            print("C'est la merde on sait pas quoi faire, mode aléatoire")
            c.discover(random.randint(0, n - 1), random.randint(0, m - 1))
            # x = input()
            # x = "next"
            # if x == "next":
            #    return "KO", "cas aléatoire need fix"
    return status, msg


# fonction qui se lance à l'éxecution
if __name__ == '__main__':
    server = "http://localhost:8000"
    group = "Groupe 42"
    members = "Styvain et Blouis"
    croco = CrocomineClient(server, group, members)
    status = "OK"
    t = Timer()
    t.start()
    while status != "Err":
        status, msg = a_game(croco)
        t.lap()
        if status != "GG":
            print(f"On s'est prix un KO")
    t.stop()
