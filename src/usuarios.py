# -*- coding: utf-8 -*-

import logging

from firebase import Firebase

logger = logging.getLogger(__name__)

class Usuarios:
    def __init__(self):
        self.db = Firebase.get_database()

        self.usuarios = {}
        self.load()


    def add(self, user):
        user_dict = user.to_dict()

        user_id = str(user["id"])

        self.usuarios[user_id] = user_dict

        self.db.child("users").set({
            user["id"]: user_dict
        })

        logger.debug("salvou")


    def has(self, user_id):
        return user_id in self.usuarios


    def get(self, user_id):
        if self.has(user_id):
            return self.usuarios[user_id]

        return None


    def values(self):
        return self.usuarios.values()


    def load(self):
        logger.info("Usuarios::load")

        self.usuarios = self.db.child("users").get().val()

        logger.info(self.usuarios)

    def __contains__(self, user_id):
        return user_id in self.usuarios
