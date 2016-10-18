# -*- coding: utf-8 -*-

import json
import logging

logger = logging.getLogger(__name__)

class Usuarios:
    def __init__(self):
        self.usuarios = {}
        self.load()


    def add(self, user):
        logger.debug("Saving: %s", str(user))
        user_id = str(user["id"])

        self.usuarios[user_id] = user.to_dict()
        self.save()


    def has(self, user_id):
        return user_id in self.usuarios


    def get(self, user_id):
        if self.has(user_id):
            return self.usuarios[user_id]

        return None


    def values(self):
        return self.usuarios.values()


    def save(self):
        with open("./usuarios.json", "w") as usuarios_file:
            print(self.usuarios)
            text = json.dumps(self.usuarios, indent=5, separators=(",", ": "))
            logger.info(text)
            usuarios_file.write(text)


    def load(self):
        logger.info("Usuarios::load")

        try:
            with open("./usuarios.json", "r") as usuarios_file:
                self.usuarios = json.loads(usuarios_file.read())
                logger.info(self.usuarios)

        except IOError as error:
            logger.debug("IOError: {}".format(error))


    def __contains__(self, user_id):
        return user_id in self.usuarios
