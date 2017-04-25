# -*- coding: utf-8 -*-

import time
import logging
import random

from operator import itemgetter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Job

from command import Command
from firebase import Firebase

logger = logging.getLogger(__name__)

class StackOvergol:

    def __init__(self):
        self.db = Firebase.get_database()

        self.abrir_job_instances = {}
        self.fechar_job_instances = {}


    @Command(onde="GRUPO", quando=False, quem=False)
    def mensalistas(self, bot, update, user, *args, **kwargs):
        # Só mostrar os usuários que ainda não estão na lista de presença e são mensalistas
        try:
            todos_usuarios = self.db.child("users").get().val().values()
        except AttributeError:
            return update.message.reply_text("Ninguém disponivel.")

        lista_mensalistas = self.getGroup(update).child("mensalistas").get().val()
        mensalistas = [user for user in todos_usuarios if str(user["id"]) in lista_mensalistas]

        if len(mensalistas) == 0:
            return update.message.reply_text("Nenhum mensalistas registrado.")

        mensalistas_ordenados = sorted(mensalistas, key=itemgetter("first_name", "last_name"))

        text = ""

        for user in mensalistas_ordenados:
            text += "- {} {}\n".format(user["first_name"], user["last_name"])

        return update.message.reply_text(text)


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def remover_mensalista(self, bot, update, user, *args, **kwargs):
        keyboard = []

        # Só mostrar os usuários que ainda não estão na lista de presença e são mensalistas
        try:
            todos_usuarios = self.db.child("users").get().val().values()
        except AttributeError:
            return update.message.reply_text("Ninguém disponivel.")

        lista_mensalistas = self.getGroup(update).child("mensalistas").get().val()
        mensalistas = [user for user in todos_usuarios if str(user["id"]) in lista_mensalistas]

        mensalistas_ordenados = sorted(mensalistas, key=itemgetter("first_name", "last_name"))

        if mensalistas_ordenados:
            for user in mensalistas_ordenados:
                botao = InlineKeyboardButton("{} {}".format(user["first_name"], user["last_name"]), callback_data=str(user["id"]))
                keyboard.append([botao])

            botao_cancelar = InlineKeyboardButton("Cancelar", callback_data="-1")
            keyboard.append([botao_cancelar])

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Remover mensalista:", reply_markup=reply_markup)

        else:
            return update.message.reply_text("Ninguém disponivel.")


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def adicionar_mensalista(self, bot, update, user, *args, **kwargs):
        keyboard = []

        # Só mostrar os usuários que ainda não estão na lista de presença e são mensalistas
        try:
            todos_usuarios = self.db.child("users").get().val().values()
        except AttributeError:
            return update.message.reply_text("Ninguém disponivel.")

        lista_mensalistas = self.getGroup(update).child("mensalistas").get().val()
        nao_mensalistas = [user for user in todos_usuarios if str(user["id"]) not in lista_mensalistas]

        nao_mensalistas_ordenados = sorted(nao_mensalistas, key=itemgetter("first_name", "last_name"))

        if nao_mensalistas_ordenados:
            for user in nao_mensalistas_ordenados:
                botao = InlineKeyboardButton("{} {}".format(user["first_name"], user["last_name"]), callback_data=str(user["id"]))
                keyboard.append([botao])

            botao_cancelar = InlineKeyboardButton("Cancelar", callback_data="-1")
            keyboard.append([botao_cancelar])

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Adicionar mensalista:", reply_markup=reply_markup)

        else:
            return update.message.reply_text("Ninguém disponivel.")


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def vai(self, bot, update, user, *args, **kwargs):
        keyboard = []

        # Só mostrar os usuários que ainda não estão na lista de presença e são mensalistas
        try:
            todos_usuarios = self.db.child("users").get().val().values()
        except AttributeError:
            return update.message.reply_text("Ninguém disponivel.")

        lista_mensalistas = self.getGroup(update).child("mensalistas").get().val()
        mensalistas = [user for user in todos_usuarios if str(user["id"]) in lista_mensalistas]

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


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def nao_vai(self, bot, update, user, *args, **kwargs):
        keyboard = []

        try:
            lista_presenca = self.getGroup(update).child("lista").get().val().values()
        except AttributeError:
            return update.message.reply_text("Lista de presença vazia.")

        lista_presenca_ordenada = sorted(lista_presenca, key=itemgetter("first_name", "last_name"))

        for user in lista_presenca_ordenada:
            user_name = "{} {}".format(user["first_name"], user["last_name"])
            botao = InlineKeyboardButton(user_name, callback_data=str(user["id"]))
            keyboard.append([botao])

        botao_cancelar = InlineKeyboardButton("Cancelar", callback_data="-1")
        keyboard.append([botao_cancelar])

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Quem nao vai?", reply_markup=reply_markup)


    def vai_nao_vai_callback(self, bot, update):
        query = update.callback_query
        query_dict = query.to_dict()

        text = query_dict["message"]["text"]

        from_user = query_dict["from"]

        group_value = self.getGroup(query).get().val()

        if not str(from_user["id"]) in group_value["admins"]:
            return

        data = query_dict["data"]

        if data == "-1":
            return bot.editMessageText(text="Cancelado",
                                       chat_id=query.message.chat_id,
                                       message_id=query.message.message_id)

        user = self.db.child("users").child(data).get().val()

        # If we can't find this user, it's problably a guest
        if not user:
            convidado = self.getGroup(query).child("lista").child(data).get().val()
            self.getGroup(query).child("lista").child(data).remove()

            message = "{} {} removido da lista de presença.".format(convidado["first_name"], convidado["last_name"])

        elif text == "Quem vai?":
            self.getGroup(query).child("farrapeiros").child(user["id"]).remove()

            user["timestamp"] = int(time.time()) - 3 * 60 * 60

            self.getGroup(query).child("lista").child(user["id"]).set(user)

            message = "{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"])

        elif text == "Remover mensalista:":
            self.getGroup(query).child("mensalistas").child(user["id"]).remove()

            message = "{} {} removido da lista de mensalistas.".format(user["first_name"], user["last_name"])

        elif text == "Adicionar mensalista:":
            nome = "{} {}".format(user["first_name"], user["last_name"])

            self.getGroup(query).child("mensalistas").child(user["id"]).set(nome)

            message = "{} adicionado à lista de mensalistas.".format(nome)

        else:
            self.getGroup(query).child("lista").child(user["id"]).remove()

            user["timestamp"] = int(time.time()) - 3 * 60 * 60

            self.getGroup(query).child("farrapeiros").child(user["id"]).set(user)

            message = "{} {} removido da lista de presença.".format(user["first_name"], user["last_name"])

        return bot.editMessageText(text=message,
                                   chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def data(self, bot, update, user, *args, **kwargs):
        if len(kwargs["args"]) != 2:
            return update.message.reply_text(
                    text="Comando incorreto. `/data <hora> <dia>`",
                    parse_mode=ParseMode.MARKDOWN
                )

        data = kwargs["args"][0] + " " + kwargs["args"][1]
        self.getGroup(update).child("data_racha").set(data)

        return update.message.reply_text("Data do proximo racha: {}".format(data))


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def resetar(self, bot, update, user, *args, **kwargs):
        self.getGroup(update).child("lista").remove()
        self.getGroup(update).child("farrapeiros").remove()
        self.getGroup(update).child("data_racha").set(" ")
        self.getGroup(update).child("registros_abertos").set(False)

        chat_id = update.message.chat_id

        if chat_id in self.abrir_job_instances:
            self.abrir_job_instances[chat_id].schedule_removal()
            self.abrir_job_instances.pop(chat_id, None)

        if chat_id in self.fechar_job_instances:
            self.fechar_job_instances[chat_id].schedule_removal()
            self.fechar_job_instances.pop(chat_id, None)

        return update.message.reply_text("Registros resetados")

    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def agendar_abrir(self, bot, update, user, *args, **kwargs):
        print(kwargs)

        if len(kwargs["args"]) != 2:
            return update.message.reply_text(
                    text="Comando incorreto. `/agendar_abrir 20:00h 01/01/17`",
                    parse_mode=ParseMode.MARKDOWN
                )

        now = time.time()
        chat_id = update.message.chat_id

        if chat_id in self.abrir_job_instances:
            self.abrir_job_instances[chat_id].schedule_removal()
            self.abrir_job_instances.pop(chat_id, None)

        hora_de_abrir = kwargs["args"][0] + " " + kwargs["args"][1]

        epoch_abrir = time.mktime(time.strptime(hora_de_abrir, "%H:%Mh %d/%m/%y"))

        if epoch_abrir < now:
            return update.message.reply_text("error: comecar < now")

        self.abrir_job_instances[chat_id] = Job(lambda bot, job: self.abrir_job(bot, job, update), epoch_abrir - now, repeat=False, context=chat_id)

        kwargs["job_queue"].put(self.abrir_job_instances[chat_id])

        self.getGroup(update).child("hora_abrir_registros").set(hora_de_abrir)

        text = "Registros abrem {}.".format(hora_de_abrir)

        return update.message.reply_text(text)


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def cancelar_abrir(self, bot, update, user, *args, **kwargs):
        chat_id = update.message.chat_id

        if chat_id in self.abrir_job_instances:
            self.abrir_job_instances[chat_id].schedule_removal()
            self.abrir_job_instances.pop(chat_id, None)

            return update.message.reply_text("Agendamento para abrir cancelado.")


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def abrir(self, bot, update, user, *args, **kwargs):
        self.getGroup(update).child("registros_abertos").set(True)

        return update.message.reply_text("Registros abertos!")


    def abrir_job(self, bot, job, update):
        self.getGroup(update).child("registros_abertos").set(True)

        chat_id = update.message.chat_id

        if chat_id in self.abrir_job_instances:
            self.abrir_job_instances[chat_id].schedule_removal()
            self.abrir_job_instances.pop(chat_id, None)

        return bot.sendMessage(job.context, text="Registros abertos!")


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def agendar_fechar(self, bot, update, user, *args, **kwargs):
        now = time.time()
        chat_id = update.message.chat_id

        if chat_id in self.fechar_job_instances:
            self.fechar_job_instances[chat_id].schedule_removal()
            self.fechar_job_instances.pop(chat_id, None)

        hora_de_fechar = kwargs["args"][0] + " " + kwargs["args"][1]

        epoch_fechar = time.mktime(time.strptime(hora_de_fechar, "%H:%Mh %d/%m/%y"))

        if epoch_fechar < now:
            return update.message.reply_text("error: terminar < now")

        self.fechar_job_instances[chat_id] = Job(lambda bot, job: self.fechar_job(bot, job, update), epoch_fechar - now, repeat=False, context=chat_id)

        kwargs["job_queue"].put(self.fechar_job_instances[chat_id])

        self.getGroup(update).child("hora_fechar_registros").set(hora_de_fechar)

        text = "Registros fecham de {}.".format(hora_de_fechar)

        return update.message.reply_text(text)


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def cancelar_fechar(self, bot, update, user, *args, **kwargs):
        chat_id = update.message.chat_id

        if chat_id in self.fechar_job_instances:
            self.fechar_job_instances[chat_id].schedule_removal()
            self.fechar_job_instances.pop(chat_id, None)

            return update.message.reply_text("Agendamento para fechar cancelado.")


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def fechar(self, bot, update, user, *args, **kwargs):
        self.getGroup(update).child("registros_abertos").set(False)

        return update.message.reply_text("Registros fechados")


    def fechar_job(self, bot, job, update):
        self.getGroup(update).child("registros_abertos").set(False)

        chat_id = update.message.chat_id

        if chat_id in self.fechar_job_instances:
            self.fechar_job_instances[chat_id].schedule_removal()
            self.fechar_job_instances.pop(chat_id, None)

        return bot.sendMessage(job.context, text="Registros fechados")


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vou_agarrar(self, bot, update, user, *args, **kwargs):
        if (self.getGroup(update).child("lista").child(user["id"]).get().val()):
            return update.message.reply_text("Você já está na lista.")

        self.getGroup(update).child("farrapeiros").child(user["id"]).remove()

        self.getGroup(update).child("lista").child(user["id"]).set({
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "timestamp": int(time.time()) - 3 * 60 * 60,
                "goleiro": True
            })

        return update.message.reply_text("{} {} adicionado à lista de goleiros.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando=False, quem=False)
    def convidado(self, bot, update, user, *args, **kwargs):
        if len(kwargs["args"]) != 2:
            return update.message.reply_text("`/convidado <nome> <sobrenome>`")

        first_name = kwargs["args"][0]
        last_name = kwargs["args"][1]

        convidado = {
            "first_name": first_name,
            "last_name": last_name,
            "timestamp": int(time.time()) - 3 * 60 * 60
        }

        convidado["id"] = user["id"] + convidado["timestamp"]

        self.getGroup(update).child("lista").child(convidado["id"]).set(convidado)

        msg = "{} {} adicionado à lista de presença.".format(convidado["first_name"], convidado["last_name"])

        return update.message.reply_text(msg)


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vou(self, bot, update, user, *args, **kwargs):
        if self.getGroup(update).child("lista").child(user["id"]).get().val():
            return update.message.reply_text("Você já está na lista.")

        self.getGroup(update).child("farrapeiros").child(user["id"]).remove()

        self.getGroup(update).child("lista").child(user["id"]).set({
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "timestamp": int(update.message.date.strftime("%s")) - 3 * 60 * 60
        })

        return update.message.reply_text("{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"]))


    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def naovou(self, bot, update, user, *args, **kwargs):
        self.getGroup(update).child("lista").child(user["id"]).remove()

        self.getGroup(update).child("farrapeiros").child(user["id"]).set({
            "id": user["id"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "timestamp": int(time.time()) - 3 * 60 * 60
        })

        output = "{} {} removido da lista de presença.".format(
            user["first_name"],
            user["last_name"]
        )

        return update.message.reply_text(output)


    def get_weakest_team(self, team):
        return min(team, key=lambda t: sum([p["stars"] for p in t]))


    def divide_teams(self, players):
        players = sorted(players, key=lambda p: p["stars"])

        teams = [[], [], [], []]

        while len(players):
            self.get_weakest_team(teams).append(players.pop())

        return teams


    def print_teams(self, update, teams):
        output = ["```text", "Ordem dos times: A x B, C, D\n"]

        for letter, team in zip(["A", "B", "C", "D"], teams):
            total = sum([p["stars"] for p in team])

            output.append("Time {:<20} {:.2f} ({:.2f})".format(
                letter,
                total,
                total / len(team)
            ))

            for i, player in enumerate(team):
                output.append("{:>2} - {:<20} {:.2f}{}".format(
                    i + 1,
                    player["first_name"] + " " + player["last_name"],
                    player["stars"],
                    "*" if "fake_stars" in player else ""
                ))

            output.append("")

        output.append("```")

        return update.message.reply_text(
                    text="\n".join(output),
                    parse_mode=ParseMode.MARKDOWN
                )


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def times(self, bot, update, user, *args, **kwargs):
        bot.sendMessage(update.message.chat_id, text="Calculando os times...")

        mensalistas = self.getGroup(update).child("mensalistas").get().val()

        try:
            lista_presenca = [j for j in self.getGroup(update).child("lista").get().val().values() if "goleiro" not in j]

        except AttributeError:
            return update.message.reply_text("Lista de presença vazia.")

        lista_mensalistas = [j for j in lista_presenca if str(j["id"]) in mensalistas]
        lista_convidados = [j for j in lista_presenca if str(j["id"]) not in mensalistas]
        lista_convidados = sorted(lista_convidados, key=itemgetter("timestamp"))

        missing_players = 24 - len(lista_mensalistas)
        lista = lista_mensalistas + lista_convidados[:missing_players]

        jogadores = []

        group_id = update.message.chat.id

        for jogador in lista:
            jogador_id = jogador["id"]

            stars = self.db.child("users/{}/groups/{}/stars".format(jogador_id, group_id)).get().val()

            if stars:
                jogador["stars"] = stars
            else:
                jogador["stars"] = 3.00
                jogador["fake_stars"] = True

            jogador["stars"] = jogador["stars"] - (random.randrange(-25, 25) / 100)

            jogadores.append(jogador)

        for i in range(len(jogadores), 24):
            fake_jogador = {
                "first_name": "Jogador",
                "last_name": str(i + 1),
                "stars": 3.00,
                "fake_stars": True
            }

            jogadores.append(fake_jogador)

        random.shuffle(jogadores)

        teams = self.divide_teams(jogadores)

        return self.print_teams(update, teams)


    @Command(onde="GRUPO", quando=False, quem=False)
    def help(self, bot, update, user, *args, **kwargs):
        admin_commands = [
            "*Comandos de Administrador:*",
            "`/abrir`: Abre os registros.",
            "`/fechar`: Fecha os registros.",
            "`/agendar_abrir HH:MMh DD/MM/YY`: Agenda o comando abrir para esta hora.",
            "`/agendar_fechar HH:MMh DD/MM/YY`: Agenda o comando fechar para esta hora.",
            "`/cancelar_abrir`: Cancela o agendamento de abrir.",
            "`/cancelar_fechar`: Cancela o agendamento de fechar.",
            "`/resetar`: Reseta algumas variáveis (listas, agendamentos, registros).",
            "`/vai`: Coloca alguém na lista de presença.",
            "`/naovai`: Remove alguém da lista de presença.",
            "`/data String`: Configura a data do racha que será mostrada com a lista de presença."
        ]

        all_commands = [
            "\n*Comandos:*",
            "`/convidado Nome Sobrenome`: Adiciona Nome Sobrenome à lista de presença.",
            "`/vou`: Coloca você na lista de presença.",
            "`/vouagarrar`: Coloca você na lista de goleiros.",
            "`/naovou`: Remove você de qualquer lista de presença.",
            "`/listar`: Imprimi a lista atual.",
        ]

        help_text = []

        if user["is_admin"]:
            help_text += admin_commands

        help_text += all_commands

        return update.message.reply_text(
                text="\n".join(help_text),
                parse_mode=ParseMode.MARKDOWN
            )


    @Command(onde="GRUPO", quando=False, quem=False)
    def listar(self, bot, update, user, *args, **kwargs):
        with_time = False

        if len(kwargs["args"]):
            with_time = kwargs["args"][0].lower() == "true"

        return update.message.reply_text(self._get_lista_presenca(update, with_time))


    @Command(onde=False, quando=False, quem=False)
    def uuid(self, bot, update, user, *args, **kwargs):
        text = "{} {}: {}".format(user["first_name"], user["last_name"], user["id"])

        return update.message.reply_text(text)


    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def fazteunome(self, bot, update, user, *args, **kwargs):
        if len(kwargs["args"]) != 6:
            return update.message.reply_text(
                    text="Comando incorreto. `/fazteunome 20:00h 01/01/17 15:00h 02/01/17 20:00h 02/01/17`",
                    parse_mode=ParseMode.MARKDOWN
                )

        self.resetar(bot, update, user, args, kwargs)

        self.agendar_abrir(bot, update, user, args, args=kwargs["args"][0:2], job_queue=kwargs["job_queue"])

        self.agendar_fechar(bot, update, user, args, args=kwargs["args"][2:4], job_queue=kwargs["job_queue"])

        self.data(bot, update, user, args, args=kwargs["args"][4:6])


    def _show_timestamp(self, user, with_time):
        if with_time:
            timestamp = time.strftime('%a %H:%M:%S', time.gmtime(user["timestamp"]))
            return "[{}] ".format(timestamp)

        return ""


    def _get_lista_presenca(self, update, with_time=False):
        group = self.getGroup(update).get().val()
        lista = []

        if "lista" in group:
            lista = group["lista"].values()
            lista = sorted(lista, key=itemgetter("timestamp"))

        hora_do_racha = ""

        if "data_racha" in group:
            hora_do_racha = group["data_racha"]

        # Adiciona o cabecalho
        linhas = [
            "Lista de Presença",
            hora_do_racha,
            "=" * 15
            ]

        # GOLEIROS
        todos_goleiros = []

        lp_goleiros = [user for user in lista if "goleiro" in user and user["goleiro"]]

        for i, user in enumerate(lp_goleiros):
            if len(todos_goleiros) == group["max_goleiros"]:
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
        lp_mensalistas = [user for user in lista if str(user["id"]) in group["mensalistas"] and "goleiro" not in user]

        for i, user in enumerate(lp_mensalistas):
            todos_jogadores.append("{} - {}{} {} (M)".format(
                i + 1,
                self._show_timestamp(user, with_time),
                user["first_name"],
                user["last_name"]
            ))

        lp_convidados = [user for user in lista if str(user["id"]) not in group["mensalistas"] and "goleiro" not in user]

        for i, user in enumerate(lp_convidados):
            if len(todos_jogadores) == group["max_jogadores"]:
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

        lp_farrapeiros = []

        if "farrapeiros" in group:
            lp_farrapeiros = group["farrapeiros"].values()
            lp_farrapeiros = sorted(lp_farrapeiros, key=itemgetter("timestamp"))

        if lp_farrapeiros:
            linhas.append("=" * 15)
            linhas.append("Farrapeiros:")

            for i, user in enumerate(lp_farrapeiros):
                linhas.append("{} - {}{} {} ({})".format(
                    i + 1,
                    self._show_timestamp(user, with_time),
                    user["first_name"],
                    user["last_name"],
                    "M" if str(user["id"]) in group["mensalistas"] else "C"
                ))

        return "\n".join(linhas)


    def isDebug(self):
        return self.db.child("debug").get().val()


    def getGroup(self, update):
        group_id = update.message.chat.id

        return self.db.child("groups").child(group_id)
