import logging

from database.firebase import database
from models.listitem import ListItem
from models.user import User
from utils import configs
from utils.teams import Teams

logger = logging.getLogger(__name__)

class Group():
    def __init__(self):
        self.job_queue = None
        self.list = []
        self.all_users = []
        self.check_in_open = False
        self.should_sync = False

        self.teams = Teams()
        self.load()

    def init(self, job_queue):
        self.job_queue = job_queue
        self.shedule_save()

    def open_check_in(self):
        self.check_in_open = True
        self.should_sync = True

    def close_check_in(self):
        self.check_in_open = False
        self.should_sync = True

    def add(self, player, is_goalkeeper=False, is_guest=False):
        if not self.__contains__(player):
            self.list.append(ListItem(
                player,
                is_goalkeeper,
                is_guest,
                hide_guest_label=configs.get("RACHA.HIDE_GUEST_LABEL"),
                hide_subscriber_label=configs.get("RACHA.HIDE_SUBSCRIBER_LABEL")
            ))
            self.list.sort()
            self.should_sync = True

    def remove(self, player):
        for i, item in enumerate(self.list):
            if item.user == player:
                self.list.pop(i)
                self.should_sync = True
                return True

        return False

    def reset(self):
        self.list = []
        self.should_sync = True

    def is_check_in_open(self):
        return self.check_in_open

    def get_user(self, data):
        for user in self.all_users:
            if data["id"] == user.uid:
                return user

        return None

    def create_user(self, data):
        user = User(uid=data["id"], rating=configs.get("RACHA.DEFAULT_RATING"), **data)

        self.all_users.append(user)
        self.should_sync = True

        return user

    def get_user_or_create(self, data):
        return self.get_user(data) or self.create_user(data)

    def calculate_teams(self):
        players = [item.user for item in self.list if not item.is_goalkeeper]

        self.teams.calculate_teams(players)
        self.should_sync = True

        return str(self.teams)

    def save(self):
        database.child("teams").set(self.teams.serialize())
        database.child("check_in_open").set(self.check_in_open)
        database.child("list").set({ item.user.uid: item.serialize() for item in self.list })
        database.child("users").set({ user.uid: user.serialize() for user in self.all_users })

        self.should_sync = False

    def load(self):
        self.check_in_open = database.child("check_in_open").get().val()
        self.list = []

        try:
            for item in database.child("list").get().each():
                values = item.val()
                user_values = values.pop("user")

                uid = user_values.pop("uid")
                first_name = user_values.pop("first_name")
                last_name = user_values.pop("last_name")

                user = User(uid, first_name, last_name, **user_values)

                listitem = ListItem(user, **values)

                self.list.append(listitem)

            self.list.sort()

        except Exception as error:
            logger.error(error)

        # TODO: load teams

        try:
            self.all_users = [User(**user.val()) for user in database.child("users").get().each()]
        except Exception as error:
            logger.error(error)

    def get_players(self, func=None):
        if func:
            return [item.user for item in self.list if func(item)]

        return self.list

    def shedule_save(self):
        def on_save_time(bot, job):
            if self.should_sync:
                self.save()

        if self.job_queue:
            self.job_queue.run_repeating(on_save_time, configs.get("SYNC_INTERVAL"))

    def find(self, term):
        return [item.user for item in self.list if term.lower() in str(item.user).lower()]

    def __str__(self):
        output = [
            "Lista de Presença",
            "=============",
        ]

        items_goalkeepers = [item for item in self.list if item.is_goalkeeper]

        if items_goalkeepers:
            output.append("Goleiros:")

            for i, item_goalkeeper in enumerate(items_goalkeepers):
                if i == configs.get("RACHA.MAX_TEAMS"):
                    output.append("\nLista de Espera (Goleiro):")

                output.append("{} - {}".format(i + 1, item_goalkeeper))

            output.append("")

        items_players = [item for item in self.list if not item.is_goalkeeper]

        max_players = configs.get("RACHA.MAX_TEAMS") * configs.get("RACHA.MAX_NUMBER_PLAYERS_TEAM")

        if items_players:
            output.append("Jogadores:")

            for i, item_player in enumerate(items_players):
                if max_players and i == max_players:
                    output.append("\nLista de Espera (Jogador):")

                output.append("{} - {}".format(i + 1, item_player))

        return "\n".join(output)

    def __repr__(self):
        return "{} list={}".format(self.__class__, self.list)

    def __contains__(self, user):
        for item in self.list:
            if user == item.user:
                return True

        return False

group = Group()
