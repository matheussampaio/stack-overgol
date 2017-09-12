import pprint
import logging

from operator import itemgetter

from utils import configs

from models.user import User
from utils.teams import Teams
from models.listitem import ListItem
from database.firebase import database

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
            self.list.append(ListItem(player, is_goalkeeper, is_guest))
            self.list.sort()
            self.should_sync = True

    def remove(self, player):
        if self.__contains__(player):
            self.list.remove(ListItem(player))
            self.should_sync = True

    def reset(self):
        self.list = []
        self.should_sync = True

    def is_check_in_open(self):
        return self.check_in_open

    def get_user(self, data):
        for user in self.all_users:
            if data["id"] == user.id:
                return user

        return None

    def create_user(self, data):
        user = User(**data)

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
        database.child("list").set({ item.user.id: item.serialize() for item in self.list })
        database.child("users").set({ user.id: user.serialize() for user in self.all_users })

        self.should_sync = False

    def load(self):
        self.check_in_open = database.child("check_in_open").get().val()
        self.list = []

        try:
            for item in database.child("list").get().each():
                values = item.val()
                user_values = values.pop("user")

                id = user_values.pop("id")
                first_name = user_values.pop("first_name")
                last_name = user_values.pop("last_name")

                user = User(id, first_name, last_name, **user_values)

                listitem = ListItem(user, **values)

                self.list.append(listitem)

            self.list.sort()

        except Exception as e:
            logger.error(e)

        # TODO: load teams

        try:
            self.all_users = [User(**user.val()) for user in database.child("users").get().each()]
        except Exception as e:
            logger.error(e)

    def get_players(self, func=None):
        if func:
            return [item.user for item in self.list if func(item)]

        return self.list

    def shedule_save(self):
        def on_save_time(bot, job):
            if self.should_sync:
                self.save()
                logger.info("sync")

        if self.job_queue:
            self.job_queue.run_repeating(on_save_time, configs.get("SYNC_INTERVAL"))

    def __str__(self):
        output = [
            "Lista de Presença",
            "=============",
        ]

        goalkeepers = [item for item in self.list if item.is_goalkeeper]

        if len(goalkeepers):
            output.append("Goleiros:")

            for i, item in enumerate(goalkeepers):
                if i == configs.get("RACHA.MAX_TEAMS"):
                    output.append("\nLista de Espera (Goleiro):")

                output.append("{} - {}".format(i + 1, item))

            output.append("")

        players = [item for item in self.list if not item.is_goalkeeper]

        if len(players):
            output.append("Jogadores:")

            for i, item in enumerate(players):
                if i == configs.get("RACHA.MAX_TEAMS") * configs.get("RACHA.MAX_NUMBER_PLAYERS_TEAM"):
                    output.append("Lista de Espera (Jogador):")

                output.append("{} - {}".format(i + 1, item))

        return "\n".join(output)

    def __repr__(self):
        return "{} id={} list={}".format(self.__class__, self.id, self.list)

    def __contains__(self, user):
        for item in self.list:
            if user == item.user:
                return True

        return False

group = Group()
