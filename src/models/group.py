import logging
import time

from database.firebase import database
from models.listitem import ListItem
from models.user import User
from utils.config import Config
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
        self.watch_updates()

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
                hide_guest_label=Config.racha_hide_guest_label(),
                hide_subscriber_label=Config.racha_hide_subscriber_label()
            ))
            self.list.sort()
            self.should_sync = True

            return True

        return False

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

    def get_user_list_item(self, user):
        for item in self.list:
            if user == item.user:
                return item

        return None

    def get_user(self, data):
        for user in self.all_users:
            if data["id"] == user.uid:
                return user

        return None

    def create_user(self, data):
        user = User(
            uid=data["id"],
            rating=Config.racha_default_rating(),
            created_at=datetime.utcnow().timestamp(),
            **data)

        self.all_users.append(user)
        self.should_sync = True

        return user

    def get_user_or_create(self, data):
        return self.get_user(data) or self.create_user(data)

    def calculate_teams(self, number_teams, team_size, team_colors, rating_range_variation, complete_team_with_fake_players, with_substitutes):
        players = [item.user for item in self.list if not item.is_goalkeeper]

        self.teams.calculate_teams(players, number_teams, team_size, team_colors, rating_range_variation, complete_team_with_fake_players)
        self.should_sync = True

        return self.teams.format(with_substitutes)

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

                listitem = ListItem(
                    user,
                    hide_guest_label=Config.racha_hide_guest_label(),
                    hide_subscriber_label=Config.racha_hide_subscriber_label(),
                    **values
                )

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
            self.job_queue.run_repeating(on_save_time, Config.sync_interval())

    def watch_updates(self):
        def update_listitem(user):
            listitem = self.get_user_list_item(user)

            if listitem:
                listitem.user = user

                self.list.sort()

                database.child("list").set({ item.user.uid: item.serialize() for item in self.list })

        def update_user(user, payload):
            if "rating" in payload:
                user.rating = payload["rating"]

            if "is_admin" in payload:
                user.is_admin = payload["is_admin"]

            if "is_subscriber" in payload:
                user.is_subscriber = payload["is_subscriber"]

            database.child("users").child(user.uid).set(user.serialize())

        def update(key, payload):
            user = self.get_user(payload)

            if user:
                update_user(user, payload)
                update_listitem(user)

            database.child("updates").child(key).remove()

        def updates_handler(bot, job):
            updates = database.child("updates").get().val()

            if not updates:
                return

            for key, changes in updates.items():
                update(key, changes["payload"])

        if self.job_queue:
            self.job_queue.run_repeating(updates_handler, Config.sync_interval())

    def find_on_list(self, term):
        return [item for item in self.list if term.lower() in str(item.user).lower()]

    def find_on_list_with_uid(self, uid):
        return [item for item in self.list if item.user.uid == uid]

    def find_on_all_players(self, term, filter_players_on_list=False):
        players = [player for player in self.all_users if term.lower() in player.full_name.lower()]

        if filter_players_on_list:
            players = [player for player in players if not self.__contains__(player)]

        return players

    def find_on_all_players_with_uid(self, uid, filter_players_on_list=False):
        players = [player for player in self.all_users if player.uid == uid]

        if filter_players_on_list:
            players = [player for player in players if not self.__contains__(player)]

        return players

    def format(self, show_aditional_info=False):
        output = [
            "```",
            "Lista de Presença",
            ""
        ]

        items_goalkeepers = [item for item in self.list if item.is_goalkeeper]

        if items_goalkeepers:
            output.append("Goleiros:")

            for i, item_goalkeeper in enumerate(items_goalkeepers):
                if i == Config.racha_max_teams():
                    output.append("\nLista de Espera (Goleiro):")

                if show_aditional_info:
                    output.append("{:>2}. {} ({})".format(i + 1, item_goalkeeper, item_goalkeeper.user.uid))
                else:
                    output.append("{:>2}. {}".format(i + 1, item_goalkeeper))

            output.append("")

        items_players = [item for item in self.list if not item.is_goalkeeper]

        max_players = Config.racha_max_teams() * Config.racha_max_number_players_team()

        if items_players:
            output.append("Jogadores:")

            for i, item_player in enumerate(items_players):
                if max_players and i == max_players:
                    output.append("\nLista de Espera (Jogador):")

                if show_aditional_info:
                    output.append("{:>2}. {} ({})".format(i + 1, item_player, item_player.user.uid))
                else:
                    output.append("{:>2}. {}".format(i + 1, item_player))

        output.append("```")

        return "\n".join(output)

    def __repr__(self):
        return "{} list={}".format(self.__class__, self.list)

    def __contains__(self, user):
        return self.get_user_list_item(user) is not None

group = Group()
