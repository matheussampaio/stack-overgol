import csv
import configs
import pyrebase

from operator import itemgetter

STACK_OVERGOL_ID = '-1001071336991'
RATINGS_FILE_NAME = 'ratings.csv'
DEBUG = False

db = pyrebase.initialize_app(configs.FIREBASE).database()

def main():
    with open(RATINGS_FILE_NAME, newline='') as ratingsfile:
        ratingsreader = csv.reader(ratingsfile, delimiter=',', quotechar='|')

        for i, row in enumerate(ratingsreader):
            if i and row[1] != '-' and row[2] != '-':
                nome = row[0]
                stars = float(row[1])
                jogador_id = row[2]

                print("{}... ".format(nome), end="")

                path = "users/{}/groups/{}/stars".format(jogador_id, STACK_OVERGOL_ID)

                oldStars = db.child(path).get().val()

                if (oldStars == stars):
                    print("OK")
                    continue

                if DEBUG:
                    print("(DEBUG) Atual: {} -> Novo: {}".format(oldStars, stars))
                    continue

                user_input = input("Atual: {} -> Novo: {} (s/n)? ".format(oldStars, stars))

                if (user_input != "s"):
                    print("Usuário não atualizado.")
                    continue

                db.child(path).set(stars)
                print("Atualizado.")



def get_missing_ratings_from_current_list(group_id, show_id=False):
    lista = db.child("groups/{}/lista".format(group_id)).get().val().values()

    lista = sorted(lista, key=itemgetter("first_name", "last_name"))

    for user in lista:
        id = user["id"]
        first_name = user["first_name"].upper()
        last_name = user["last_name"].upper()

        rating = db.child("users/{}/groups/{}/stars".format(id, group_id)).get().val()

        if (rating is None):
            if show_id:
                output = "{:10} - ".format(id)
            else:
                output = ""

            output += ",{} {},,,{}".format(first_name, last_name, user["id"])

            print(output)


# Firebase Admin: Search User
# firebase().database().ref('/users').once('value', (snapshot) => {
#     let result = '';
#     const search = 'lindemberg'.toLowerCase();
#
#     const users = snapshot.val();
#
#     for (let key in users) {
#         const user = users[key];
#
#         const nome = `${user.first_name} ${user.last_name}`;
#
#         if (nome.toLowerCase().indexOf(search) !== -1) {
#             result += `${nome.toUpperCase()}\t\t\t${user.id}\n`;
#         }
#     }
#
#     console.log(result);
# });

if __name__ == "__main__":
    get_missing_ratings_from_current_list(STACK_OVERGOL_ID)

    # main()
