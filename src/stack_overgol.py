# -*- coding: utf-8 -*-

import time
import logging
from operator import itemgetter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Job

from command import Command
from firebase import Firebase

logger = logging.getLogger(__name__)

class StackOvergol:

    def __init__(self):
        self.db = Firebase.get_database()

        self.comecar_job = None
        self.terminar_job = None

        self._load_configs()

    @Command(onde="GRUPO", quando="ABERTO", quem="ADMIN")
    def vai(self, bot, update, user, *args, **kwargs):
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
    def nao_vai(self, bot, update, user, *args, **kwargs):
        keyboard = []

        try:
            lista_presenca = self.db.child("lista").get().val().values()
        except AttributeError:
            return update.message.reply_text("Lista de presença vazia.")

        lista_presenca_ordenada = sorted(lista_presenca, key=itemgetter("first_name", "last_name"))

        for user in lista_presenca_ordenada:
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

        # If we can't find this user, it's problably a guest
        if not user:
            convidado = self.db.child("lista").child(data).get().val()
            self.db.child("lista").child(data).remove()

            message = "{} {} removido da lista de presença.".format(convidado["first_name"], convidado["last_name"])

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


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def abrir(self, bot, update, user, *args, **kwargs):
        self.db.child("registros_abertos").set(True)
        return update.message.reply_text("Registros abertos!")


    def abrir_job(self, bot, job):
        self.db.child("registros_abertos").set(True)
        return bot.sendMessage(job.context, text="Registros abertos!")


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def data(self, bot, update, user, *args, **kwargs):
        data = kwargs["args"][0] + " " + kwargs["args"][1]
        self.db.child("data_racha").set(data)

        return update.message.reply_text("Data do proximo racha: {}".format(data))


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def resetar(self, bot, update, user, *args, **kwargs):
        self.db.child("lista").remove()
        self.db.child("farrapeiros").remove()
        return update.message.reply_text("Registros resetados")


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def agendar(self, bot, update, user, *args, **kwargs):
        now = time.time()
        chat_id = update.message.chat_id

        if self.comecar_job:
            self.comecar_job.schedule_removal()
            self.comecar_job = None

        if self.terminar_job:
            self.terminar_job.schedule_removal()
            self.terminar_job = None

        hora_de_abrir = kwargs["args"][0] + " " + kwargs["args"][1]
        hora_de_fechar = kwargs["args"][2] + " " + kwargs["args"][3]

        epoch_comecar = time.mktime(time.strptime(hora_de_abrir, "%H:%Mh %d/%m/%y"))
        epoch_terminar = time.mktime(time.strptime(hora_de_fechar, "%H:%Mh %d/%m/%y"))

        logging.info("now %d", now)
        logging.info("comecar %d", epoch_comecar)
        logging.info("terminar %d", epoch_terminar)

        if epoch_comecar < now:
            return update.message.reply_text("error: comecar < now")
        elif epoch_terminar < now:
            return update.message.reply_text("error: terminar < now")
        elif epoch_comecar > epoch_terminar:
            return update.message.reply_text("error: comecar > terminar")

        self.comecar_job = Job(self.abrir_job, epoch_comecar - now, repeat=False, context=chat_id)
        self.terminar_job = Job(self.fechar_job, epoch_terminar - now, repeat=False, context=chat_id)

        if "job_queue" not in kwargs:
            return update.message.reply_text("error: cant find job_queue")

        kwargs["job_queue"].put(self.comecar_job)
        kwargs["job_queue"].put(self.terminar_job)

        self.db.child("hora_comecar_registros").set(hora_de_abrir)
        self.db.child("hora_terminar_registros").set(hora_de_fechar)

        text = "Racha agendado. Registros começam {} e fecham de {}.".format(
                    hora_de_abrir,
                    hora_de_fechar
                )

        return update.message.reply_text(text)


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def fechar(self, bot, update, user, *args, **kwargs):
        self.db.child("registros_abertos").set(False)
        return update.message.reply_text("Registros fechados")


    def fechar_job(self, bot, job):
        self.db.child("registros_abertos").set(False)
        return bot.sendMessage(job.context, text="Registros fechados")


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vou_agarrar(self, bot, update, user, *args, **kwargs):
        user = self.db.child("lista").child(user["id"]).get().val()

        if (user):
            return update.message.reply_text("Você já está na lista.")

        self.db.child("farrapeiros").child(user["id"]).remove()

        user["timestamp"] = int(time.time()) - 3 * 60 * 60
        user["goleiro"] = True

        self.db.child("lista").child(user["id"]).set(user)

        return update.message.reply_text("{} {} adicionado à lista de goleiros.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando="ABERTO", quem="ADMIN")
    def convidado(self, bot, update, user, *args, **kwargs):
        first_name = kwargs["args"][0]
        last_name = kwargs["args"][1]

        convidado = {
            "first_name": first_name,
            "last_name": last_name,
            "timestamp": int(time.time()) - 3 * 60 * 60
        }

        convidado["id"] = user["id"] + convidado["timestamp"]

        logger.info("convidado ojb")
        logger.info(convidado)

        self.db.child("lista").child(convidado["id"]).set(convidado)

        msg = "{} {} adicionado à lista de presença.".format(convidado["first_name"], convidado["last_name"])

        return update.message.reply_text(msg)


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vou(self, bot, update, user, *args, **kwargs):
        user = self.db.child("lista").child(user["id"]).get().val()

        if (user):
            return update.message.reply_text("Você já está na lista.")

        self.db.child("farrapeiros").child(user["id"]).remove()

        user["timestamp"] = int(time.time()) - 3 * 60 * 60

        self.db.child("lista").child(user["id"]).set(user)

        return update.message.reply_text("{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def naovou(self, bot, update, user, *args, **kwargs):
        self.db.child("lista").child(user["id"]).remove()

        user["timestamp"] = int(time.time()) - 3 * 60 * 60

        self.db.child("farrapeiros").child(user["id"]).set(user)

        return update.message.reply_text("{} {} removido da lista de presença.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando=False, quem=False)
    def help(self, bot, update, user, *args, **kwargs):
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
    def listar(self, bot, update, user, *args, **kwargs):
        return update.message.reply_text(self._get_lista_presenca())


    @Command(onde="GRUPO", quando=False, quem=False)
    def uuid(self, bot, update, user, *args, **kwargs):
        text = "{} {}: {}".format(user["first_name"], user["last_name"], user["id"])

        return update.message.reply_text(text)


    def _load_configs(self):
        self.DEBUG = self.db.child("debug").get().val()

        config = self.db.child("config").get().val()

        if not config:
            config = {
                "debug": False,
                "group_id": -1,
                "max_goleiros": 2,
                "max_jogadores": 24
            }

            self.db.child("config").set(config)

        if "admins" not in config:
            config["admins"] = {}

        if "mensalistas" not in config:
            config["mensalistas"] = {}

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

        hora_do_racha = self.db.child("data_racha").get().val()

        if not hora_do_racha:
            hora_do_racha = ""

        # Adiciona o cabecalho
        linhas = [
            "Lista de Presença",
            hora_do_racha,
            "=" * 15
            ]

        # GOLEIROS
        todos_goleiros = []

        logger.info(lista)

        lp_goleiros = [user for user in lista if "goleiro" in user and user["goleiro"]]

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

