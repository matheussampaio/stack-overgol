import csv
import configs
import pyrebase

group_id = '-1001071336991'

def main():
    db = pyrebase.initialize_app(configs.FIREBASE).database()

    with open('ratings2.csv', newline='') as ratingsfile:
        ratingsreader = csv.reader(ratingsfile, delimiter=',', quotechar='|')

        for i, row in enumerate(ratingsreader):
            if i and row[4] != '-':
                print(i, row)

                jogador_id = row[4]
                stars = float(row[2])

                db.child("users/{}/groups/{}".format(jogador_id, group_id)).update({
                    "stars": stars
                })


if __name__ == "__main__":
    main()
