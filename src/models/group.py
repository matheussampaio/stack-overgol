import pprint
import logging

from operator import itemgetter

from utils import configs
from models.user import User
from models.listitem import ListItem
from database.firebase import database
from metaclasses.singleton import Singleton

logger = logging.getLogger(__name__)

class Group(metaclass=Singleton):
    def __init__(self):
        self.list = []
        self.all_users = []
        self.check_in_open = False

        self.load()

    def open_check_in(self):
        self.check_in_open = True
        self.save()

    def close_check_in(self):
        self.check_in_open = False
        self.save()

    def add(self, player, is_goalkeeper=False, is_guest=False):
        if not self.__contains__(player):
            self.list.append(ListItem(player, is_goalkeeper, is_guest))
            self.list.sort(reverse=True) #key=itemgetter("is_goalkeeper", "is_guest", "timestamp"))
            self.save()

    def remove(self, player):
        if self.__contains__(player):
            self.list.remove(ListItem(player))
            self.save()

    def reset(self):
        self.list = []
        self.save()

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

        return user

    def get_user_or_create(self, data):
        return self.get_user(data) or self.create_user(data)

    def save(self):
        database.child("check_in_open").set(self.check_in_open)
        database.child("list").set({ item.user.id: item.serialize() for item in self.list })
        database.child("users").set({ user.id: user.serialize() for user in self.all_users })

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

        except Exception as e:
            logger.error(e)

        try:
            self.all_users = [User(**user.val()) for user in database.child("users").get().each()]
        except Exception as e:
            logger.error(e)

    def __str__(self):
        output = [
            "Lista de Presença",
            "=============",
        ]

        for i, item in enumerate(self.list):
            output.append("{} - {}".format(i + 1, item))

        return "\n".join(output)

    def __repr__(self):
        return "{} id={} list={}".format(self.__class__, self.id, self.list)

    def __contains__(self, user):
        for item in self.list:
            if user == item.user:
                return True

        return False
