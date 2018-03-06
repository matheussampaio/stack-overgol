import csv
import pyrebase

from operator import itemgetter

from utils import configs
from database.firebase import database

STACK_OVERGOL_ID = '-1001071336991'
RATINGS_FILE_NAME = 'ratings.csv'
DEBUG = False

def main():
    with open(RATINGS_FILE_NAME, newline='') as ratingsfile:
        ratingsreader = csv.reader(ratingsfile, delimiter=',', quotechar='|')

        for i, row in enumerate(ratingsreader):
            if not i or not row[0]:
                continue

            try:
                value = int(row[5])
            except:
                value = 0

            user = database.child("users/{}".format(row[0])).get().val()

            if not user:
                database.child("users/{}".format(row[0])).set({
                    "first_name": row[1],
                    "last_name": row[2],
                    "rating": float(row[3]) or 3,
                    "is_admin": row[4] == '1',
                    "is_subscriber": row[5] == '1',
                    "uid": int(row[0])
                })
            else:
                database.child("users/{}".format(row[0])).update({
                    "rating": float(row[3]) or 3,
                    "is_admin": row[4] == '1',
                    "is_subscriber": row[5] == '1'
                })

            user = database.child("list/{}".format(row[0])).get().val()

            if user:
                database.child("list/{}/user".format(row[0])).update({
                    "rating": float(row[3]) or 3,
                    "is_admin": row[4] == '1',
                    "is_subscriber": row[5] == '1'
                })

def get_missing_ratings_from_current_list(group_id, show_id=False):
    lista = database.child("groups/{}/lista".format(group_id)).get().val().values()

    lista = sorted(lista, key=itemgetter("first_name", "last_name"))

    for user in lista:
        id = user["id"]
        first_name = user["first_name"].upper()
        last_name = user["last_name"].upper()

        rating = database.child("users/{}/groups/{}/stars".format(id, group_id)).get().val()

        if (rating is None):
            if show_id:
                output = "{:10} - ".format(id)
            else:
                output = ""

            output += ",{} {},,,{}".format(first_name, last_name, user["id"])

            print(output)

def update_users_object():
    subscribers = database.child("groups/{}/mensalistas".format(STACK_OVERGOL_ID)).get().val()

    users = database.child("users").get().val().values()

    new_users_format = {}

    for user in users:
        try:
            rating = user["groups"][STACK_OVERGOL_ID]["stars"]
        except:
            rating = 3.0

        new_user = {
            "first_name": user["first_name"],
            "id": user["id"],
            "is_admin": False,
            "is_subscriber": str(user["id"]) in subscribers,
            "last_name": user["last_name"],
            "rating": rating,
            "strikes": 0
        }

        new_users_format[new_user["id"]] = new_user

    database.child("refactor/users").set(new_users_format)



if __name__ == "__main__":
    # get_missing_ratings_from_current_list(STACK_OVERGOL_ID)

    main()

    # update_users_object()
