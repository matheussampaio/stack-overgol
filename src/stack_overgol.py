# -*- coding: utf-8 -*-

import time
import logging
from operator import itemgetter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from command import Command
from firebase import Firebase

logger = logging.getLogger(__name__)

class StackOvergol:

    def __init__(self):
        self.db = Firebase.get_database()

        self._load_configs()

    @Command(onde="GRUPO", quando="ABERTO", quem="ADMIN")
    def vai(self, bot, update, user):
        keyboard = []

        # Só mostrar os usuários que ainda não estão na lista de presença e são mensalistas
        try:
            todos_usuarios = self.db.child("users").get().val().values()
        except AttributeError:
            return update.message.reply_text("Ninguém disponivel.")

        mensalistas = [ user for user in todos_usuarios if user["id"] in self.LISTA_MENSALISTAS ]

        mensalistas_ordenados = sorted(mensalistas, key=itemgetter("first_name", "last_name"))

        if mensalistas_ordenados:
            for user in mensalistas_ordenados:
                botao = InlineKeyboardButton("{} {}".format(user["first_name"], user["last_name"]), callback_data=str(user["id"]))
                keyboard.append([ botao ])

            botao_cancelar = InlineKeyboardButton("Cancelar", callback_data="-1")
            keyboard.append([ botao_cancelar ])

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Quem vai?", reply_markup=reply_markup)

        else:
            return update.message.reply_text("Ninguém disponivel.")


    @Command(onde="GRUPO", quando="ABERTO", quem="ADMIN")
    def nao_vai(self, bot, update, user):
        keyboard = []

        try:
            lista_presenca = self.db.child("lista").get().val().values()
        except AttributeError:
            return update.message.reply_text("Lista de presença vazia.")

        for user in lista_presenca:
            user_name = "{} {}".format(user["first_name"], user["last_name"])
            botao = InlineKeyboardButton(user_name, callback_data=str(user["id"]))
            keyboard.append([ botao ])

        botao_cancelar = InlineKeyboardButton("Cancelar", callback_data="-1")
        keyboard.append([ botao_cancelar ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Quem nao vai?", reply_markup=reply_markup)


    def vai_nao_vai_callback(self, bot, update):
        query = update.callback_query
        query_dict = query.to_dict()

        text = query_dict["message"]["text"]

        from_user = query_dict["from"]

        if not from_user["id"] in self.LISTA_ADMINS:
            return

        data = query_dict["data"]

        if data == "-1":
            return bot.editMessageText(text="Cancelado",
                                       chat_id=query.message.chat_id,
                                       message_id=query.message.message_id)

        user = self.db.child("users").child(data).get().val()
        if not user:
            message = "Nenhum usuário com id: {}".format(data)

        elif text == "Quem vai?":
            self.db.child("farrapeiros").child(user["id"]).remove()

            user["timestamp"] = int(time.time()) - 3 * 60 * 60

            self.db.child("lista").child(user["id"]).set(user)

            message = "{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"])
        else:
            self.db.child("lista").child(user["id"]).remove()

            user["timestamp"] = int(time.time()) - 3 * 60 * 60

            self.db.child("farrapeiros").child(user["id"]).set(user)

            message = "{} {} removido da lista de presença.".format(user["first_name"], user["last_name"])

        return bot.editMessageText(text=message,
                                   chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)


    @Command(onde="GRUPO", quando="FECHADO", quem="ADMIN")
    def comecar(self, bot, update, user):
        self.db.child("registros_abertos").set(True)
        self.db.child("lista").remove()
        self.db.child("farrapeiros").remove()

        return update.message.reply_text("Registros abertos!")


    @Command(onde="GRUPO", quando="ABERTO", quem="ADMIN")
    def terminar(self, bot, update, user):
        self.db.child("registros_abertos").set(False)

        lista_final = self._get_lista_presenca()

        text = "Registro encerrado!\n\nLISTA FINAL:\n{}".format(lista_final)

        return update.message.reply_text(text)


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vou_agarrar(self, bot, update, user):
        self.db.child("farrapeiros").child(user["id"]).remove()

        user["timestamp"] = int(time.time()) - 3 * 60 * 60
        user["goleiro"] = True

        self.db.child("lista").child(user["id"]).set(user)

        return update.message.reply_text("{} {} adicionado à lista de goleiros.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vou(self, bot, update, user):
        self.db.child("farrapeiros").child(user["id"]).remove()

        user["timestamp"] = int(time.time()) - 3 * 60 * 60

        self.db.child("lista").child(user["id"]).set(user)

        return update.message.reply_text("{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def naovou(self, bot, update, user):
        self.db.child("lista").child(user["id"]).remove()

        user["timestamp"] = int(time.time()) - 3 * 60 * 60

        self.db.child("farrapeiros").child(user["id"]).set(user)

        return update.message.reply_text("{} {} removido da lista de presença.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando=False, quem=False)
    def help(self, bot, update, user):
        admin_commands = [
            "Comandos de Bruno:",
            "/comecar: Começa os registros e reseta todas as listas.",
            "/terminar: Termina os registros e imprimi a lista final.",
            "/vai: Coloca alguém na lista de presença.",
            "/naovai: Remove alguém da lista de presença.",
        ]

        all_commands = [
            "\nComandos:",
            "/vou: Coloca você na lista de presença.",
            "/vouagarrar: Coloca você na lista de goleiros.",
            "/naovou: Remove você de qualquer lista de presença.",
            "/listar: Imprimi a lista atual.",
        ]

        help_text = all_commands

        return update.message.reply_text("\n".join(help_text))


    @Command(onde="GRUPO", quando=False, quem=False)
    def listar(self, bot, update, user):
        return update.message.reply_text(self._get_lista_presenca())


    @Command(onde="GRUPO", quando=False, quem=False)
    def uuid(self, bot, update, user):
        text = "{} {}: {}".format(user["first_name"], user["last_name"], user["id"])

        return update.message.reply_text(text)


    def _load_configs(self):
        self.DEBUG = self.db.child("debug").get().val()

        config = self.db.child("config").get().val()

        if not config:
            config = {
                "debug": False,
                "group_id": -1,
                "admins": [],
                "mensalistas": [],
                "max_goleiros": 2,
                "max_jogadores": 24
            }

            self.db.child("config").set(config)

        self.GROUP_ID = config["group_id"]
        self.LISTA_ADMINS = [ int(key) for key in config["admins"].keys() ]
        self.LISTA_MENSALISTAS = [ int(key) for key in config["mensalistas"].keys() ]
        self.MAX_VAGAS_GOLEIROS = config["max_goleiros"]
        self.MAX_VAGAS_JOGADORES = config["max_jogadores"]


    def _show_timestamp(self, user, with_time):
        if with_time:
            timestamp = time.strftime('%a %H:%M:%S', time.gmtime(user["timestamp"]))
            return "[{}] ".format(timestamp)

        return ""


    def _get_lista_presenca(self, with_time=False):
        try:
            lista = self.db.child("lista").get().val().values()
            lista = sorted(lista, key=itemgetter("timestamp"))
        except AttributeError:
            lista = []

        self._load_configs()

        # Adiciona o cabecalho
        linhas = [
            "Lista de Presença",
            "=" * 15
            ]

        # GOLEIROS
        todos_goleiros = []

        logger.info(lista)

        lp_goleiros = [ user for user in lista if "goleiro" in user and user["goleiro"] ]

        for i, user in enumerate(lp_goleiros):
            if len(todos_goleiros) == self.MAX_VAGAS_GOLEIROS:
                todos_goleiros.append("Lista de Espera (Goleiro):")

            todos_goleiros.append("{} - {}{} {}".format(
                i + 1,
                self._show_timestamp(user, with_time),
                user["first_name"],
                user["last_name"]
            ))

        linhas.append("Goleiros:")
        if len(todos_goleiros):
            linhas += todos_goleiros
        else:
            linhas.append("----")
        linhas.append("=" * 15)


        # JOGADORES
        todos_jogadores = []
        lp_mensalistas = [ user for user in lista if user["id"] in self.LISTA_MENSALISTAS and "goleiro" not in user ]

        for i, user in enumerate(lp_mensalistas):
            todos_jogadores.append("{} - {}{} {} (M)".format(
                i + 1,
                self._show_timestamp(user, with_time),
                user["first_name"],
                user["last_name"]
            ))


        lp_convidados = [ user for user in lista if user["id"] not in self.LISTA_MENSALISTAS and "goleiro" not in user ]
        for i, user in enumerate(lp_convidados):
            if len(todos_jogadores) == self.MAX_VAGAS_JOGADORES:
                todos_jogadores.append("\nLista de Espera:")

            todos_jogadores.append("{} - {}{} {} (C)".format(
                i + 1 + len(lp_mensalistas),
                self._show_timestamp(user, with_time),
                user["first_name"],
                user["last_name"]
            ))

        linhas.append("Jogadores:")
        if len(todos_jogadores):
            linhas += todos_jogadores
        else:
            linhas.append("----")

        try:
            lp_farrapeiros = self.db.child("farrapeiros").get().val().values()
            lp_farrapeiros = sorted(lp_farrapeiros, key=itemgetter("timestamp"))
        except AttributeError:
            lp_farrapeiros = []


        if lp_farrapeiros:
            linhas.append("=" * 15)
            linhas.append("Farrapeiros:")

            for i, user in enumerate(lp_farrapeiros):
                linhas.append("{} - {}{} {} ({})".format(
                    i + 1,
                    self._show_timestamp(user, with_time),
                    user["first_name"],
                    user["last_name"],
                    "M" if user["id"] in self.LISTA_MENSALISTAS else "C"
                ))

        return "\n".join(linhas)

