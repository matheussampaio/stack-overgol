import csv
import configs
import pyrebase

from operator import itemgetter

STACK_OVERGOL_ID = '-1001071336991'

db = pyrebase.initialize_app(configs.FIREBASE).database()

def main():
    with open('ratings2.csv', newline='') as ratingsfile:
        ratingsreader = csv.reader(ratingsfile, delimiter=',', quotechar='|')

        for i, row in enumerate(ratingsreader):
            if i and row[4] != '-':
                print(i, row)

                jogador_id = row[4]
                stars = float(row[2])

                db.child("users/{}/groups/{}".format(jogador_id, STACK_OVERGOL_ID)).update({
                    "stars": stars
                })

def get_current_list_and_ratings(group_id, show_id=False):
    lista = db.child("groups/{}/lista".format(group_id)).get().val().values()

    lista = sorted(lista, key=itemgetter("first_name", "last_name"))

    for user in lista:
        id = user["id"]
        first_name = user["first_name"]
        last_name = user["last_name"]

        rating = db.child("users/{}/groups/{}/stars".format(id, group_id)).get().val()

        if (rating is None):
            if show_id:
                output = "{:10} - ".format(id)
            else:
                output = ""

            output += "{} {}".format(first_name, last_name)

            print(output)

if __name__ == "__main__":
    get_current_list_and_ratings('-1001071336991')
