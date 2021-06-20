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


def generate_map(size: (int, int), percent_animal: (int, int, int)):
    """
    call this function to generate new map in ../serveur/grilles/
    :param size:
    :param percent_animal:  Order is (tiger_count, shark_count, croco_count)
    """
    largeur = size[0]
    hauteur = size[1]

    map = [[list(constants.FIELD_CHAR.values())[random.randint(0, 1)] for x in range(largeur)] for y in range(hauteur)]

    percent_tiger = percent_animal[0]
    percent_shark = percent_animal[1]
    percent_croco = percent_animal[2]
    total = percent_tiger + percent_shark + percent_croco
    if total > 100:
        print(f"err: percent animal ({total}) is > 100")

    nb_dict = {
        "tigre": int((largeur * hauteur * percent_tiger) / 100),
        "requin": int((largeur * hauteur * percent_shark) / 100),
        "crocodile" : int((largeur * hauteur * percent_croco) / 100)
    }

    for name in constants.ANIMAL_CHAR.keys():
        put_random_animal(map=map, animal=name, nombre=nb_dict.get(name))

    with open(f"../serveur/grilles/grille_{percent_croco}_{percent_shark}_{percent_shark}.txt", 'w+') as out_file:
        out_file.write(f"grille {percent_croco} {percent_shark} {percent_shark}\n")
        out_file.write(f"{hauteur} {largeur}\n")
        out_file.write("0 0\n") #TODO: what is 2nd line ?

        for r in map:
            for c in r:
                out_file.write(f"{c} ")
            out_file.write("\n")
