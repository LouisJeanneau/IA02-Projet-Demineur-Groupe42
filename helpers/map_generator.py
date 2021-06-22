import random
import constants


def put_random_animal(map, animal: str, nombre: int):
    """
    this function place corresponding "animal" char randomly on "map"
    :param map: 2d array
    :param animal:
    :param nombre:
    """
    for i in range(nombre):
        x = random.randint(0, len(map) - 1)
        y = random.randint(0, len(map[0]) - 1)
        # TODO: should we specify W like example map ?
        if map[x][y] not in constants.ANIMAL_CHAR.values():
            map[x][y] = constants.ANIMAL_CHAR.get(animal)
        else:
            nombre = nombre + 1


def generate_map(size: (int, int), percent_animal: (int, int, int, int)):
    """
    call this function to generate new map in ../serveur/grilles/
    :param size:
    :param percent_animal:  Order is (tiger_count, shark_count, croco_count, water_croco_count)
    """
    hauteur = size[0]
    largeur = size[1]

    map = [[list(constants.FIELD_CHAR.values())[random.randint(0, 1)] for y in range(largeur)] for x in range(hauteur)]

    percent_tiger = percent_animal[0]
    percent_shark = percent_animal[1]
    percent_croco = percent_animal[2]
    percent_water_croco = percent_animal[3]
    total = percent_tiger + percent_shark + percent_croco + percent_water_croco
    if total > 100:
        print(f"err: percent animal ({total}) is > 100")

    nb_dict = {
        "tigre": int((largeur * hauteur * percent_tiger) / 100),
        "requin": int((largeur * hauteur * percent_shark) / 100),
        "crocodile": int((largeur * hauteur * percent_croco) / 100),
        "water_crocodile": int((largeur * hauteur * percent_water_croco) / 100)
    }

    for name in constants.ANIMAL_CHAR.keys():
        put_random_animal(map=map, animal=name, nombre=nb_dict.get(name))

    # Create a safe start point
    safe_x = random.randint(0, len(map) - 1)
    safe_y = random.randint(0, len(map[0]) - 1)
    map[safe_x][safe_y] = list(constants.FIELD_CHAR.values())[random.randint(0, 1)]
    for (k, l) in constants.VOISINS:
        if 0 <= safe_x + k < hauteur:
            if 0 <= safe_y + l < largeur:
                map[safe_x + k][safe_y + l] = list(constants.FIELD_CHAR.values())[random.randint(0, 1)]

    with open(f"../serveur/grilles/grille_{percent_tiger}_{percent_shark}_{percent_croco}_{percent_water_croco}.croco",
              'w+') as out_file:
        out_file.write(f"grille {percent_tiger}_{percent_shark}_{percent_croco}_{percent_water_croco}\n")
        out_file.write(f"{hauteur} {largeur}\n")
        out_file.write(f"{safe_x} {safe_y}\n")

        for r in map:
            for c in r:
                out_file.write(f"{c} ")
            out_file.write("\n")
