# -*- coding: utf-8 -*-

import time
import logging
from operator import itemgetter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from firebase import Firebase

logger = logging.getLogger(__name__)

class StackOvergol:

    def __init__(self):
        self.db = Firebase.get_database()

        config = self.db.child("config").get().val()

        self.DEBUG = config["debug"]
        self.GROUP_ID = config["group_id"]
        self.LISTA_ADMINS = [ int(key) for key in config["admins"].keys() ]
        self.LISTA_MENSALISTAS = [ int(key) for key in config["mensalistas"].keys() ]
        self.MAX_VAGAS_GOLEIROS = config["max_goleiros"]
        self.MAX_VAGAS_JOGADORES = config["max_jogadores"]

        self.registros_abertos = self.DEBUG or self.db.child("registros_abertos").get().val()


    def vai(self, bot, update):
        """
        @Comando: /vai
        @Quem: A

        Quando o admin enviar o comando, o bot deve mostrar a lista de usuários
        que não estão na lista de presença. O usuário deve selecionar um dentre
        as opções. O bot deve colocar o usuário selecionado na lista de
        presença.
        """

        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not user["id"] in self.LISTA_ADMINS:
            return

        if not self.db.child("registros_abertos").get().val():
            return update.message.reply_text("Os registros estão fechados.")

        keyboard = []

        # Só mostrar os usuários que ainda não estão na lista de presença e são mensalistas
        try:
            todos_usuarios = self.db.child("users").get().val().values()
        except Exception:
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


    def nao_vai(self, bot, update):
        """
        @Comando: /naovai
        @Quem: A

        Quando o adimin enviar o comando, o bot irá mostrar a lista de usuários
        que estão na lista de presença. O usuário deverá escolher um dentre as
        opções. O bot deve retirar o usuário selecionado da lista de presença.
        """
        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not user["id"] in self.LISTA_ADMINS:
            return

        if not self.db.child("registros_abertos").get().val():
            return update.message.reply_text("Os registros estão fechados.")

        keyboard = []

        try:
            lista_presenca = self.db.child("lista").get().val().values()
        except Exception:
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

            user["timestamp"] = time.strftime("%X")

            self.db.child("lista").child(user["id"]).set(user)

            message = "{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"])
        else:
            self.db.child("lista").child(user["id"]).remove()

            user["timestamp"] = time.strftime("%X")

            self.db.child("farrapeiros").child(user["id"]).set(user)

            message = "{} {} removido da lista de presença.".format(user["first_name"], user["last_name"])

        return bot.editMessageText(text=message,
                                   chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)


    def comecar(self, bot, update):
        """
        @Comando: /comecar
        @Quem: A

        Quando o admin enviar o comando, as listas são resetados e os comandos
        de registros são liberados.
        """

        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not user["id"] in self.LISTA_ADMINS:
            return

        if self.db.child("registros_abertos").get().val():
            return update.message.reply_text("Os registros já estão abertos.")

        self.db.child("registros_abertos").set(True)
        self.db.child("lista").remove()
        self.db.child("farrapeiros").remove()

        return update.message.reply_text("Registros abertos!")


    def terminar(self, bot, update):
        """
        @Comando: /terminar
        @Quem: A

        Quando o admin enviar o comando, os registros serão encerrados e a
        lista final é impressa.

        @TODO: Deve definir os times.
        @TODO: Deve sortear a ordem dos times (quem joga primeiro).
        """

        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not user["id"] in self.LISTA_ADMINS:
            return

        if not self.db.child("registros_abertos").get().val():
            return update.message.reply_text("Os registros já estão fechados.")

        self.db.child("registros_abertos").set(False)

        lista_final = self._get_lista_presenca()

        text = "Registro encerrado!\n\nLISTA FINAL:\n{}".format(lista_final)

        return update.message.reply_text(text)


    def vou_agarrar(self, bot, update):
        """
        @Comando: /vouagarrar
        @Quem: M, C

        Quando o usuário enviar o comando, se não estiver em nenhuma lista,
        adiciona o usuário na lista de goleiros.
        """

        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            return update.message.reply_text("Os registros estão fechados.")

        self.db.child("farrapeiros").child(user["id"]).remove()

        user["timestamp"] = time.strftime("%X")
        user["goleiro"] = True

        self.db.child("lista").child(user["id"]).set(user)

        update.message.reply_text("{} {} adicionado à lista de goleiros.".format(user["first_name"], user["last_name"]))


    def vou(self, bot, update):
        """
        @Comando: /vou
        @Quem: M, C

        Quando o usúario digitar o comando, se não estiver em nenhuma lista,
        será adicionado.
        """

        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not self.db.child("registros_abertos").get().val():
            return update.message.reply_text("Os registros estão fechados.")

        self.db.child("farrapeiros").child(user["id"]).remove()

        user["timestamp"] = time.strftime("%X")

        self.db.child("lista").child(user["id"]).set(user)

        update.message.reply_text("{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"]))


    def naovou(self, bot, update):
        """
        @Comando: /naovou
        @Quem: Mensalistas, Goleiros e Convidados

        Quando o usuário enviar o comando, será removido da lista
        correspondente.
        """

        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not self.db.child("registros_abertos").get().val():
            return update.message.reply_text("Os registros estão fechados.")

        self.db.child("lista").child(user["id"]).remove()

        user["timestamp"] = time.strftime("%X")

        self.db.child("farrapeiros").child(user["id"]).set(user)

        update.message.reply_text("{} {} removido da lista de presença.".format(user["first_name"], user["last_name"]))


    def help(self, bot, update):

        self._save_user(update.message.from_user)

        if not self._is_valid_msg(update):
            return

        admin_commands = [
            "Comandos de Bruno:",
            "/comecar: Começa os registros e reseta todas as listas.",
            "/terminar: Termina os registros e imprimi a lista final.",
            "/vai: Coloca alguém na lista de presença.",
            "/naovai: Remove alguém da lista de presença.",
        ]

        all_commands = [
            "\nComandos do Resto:",
            "/vou: Coloca você na lista de presença.",
            "/vouagarrar: Coloca você na lista de goleiros.",
            "/naovou: Remove você de qualquer lista de presença.",
            "/listar: Imprimi a lista atual.",
        ]

        wip_commands = [
            # "\nWorking in Progress:",
        ]

        help_text = admin_commands + all_commands + wip_commands

        update.message.reply_text("\n".join(help_text))


    def listar(self, bot, update):
        """
        @Comando: /listar
        @Quem: M, C

        Quando o usuário digitar o comando, será impresso a lista atual
        dos goleiros, mensalistas e convidado. Também deve ser impresso a
        situação atual dos registros (Aberto ou Fechado).
        """

        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        if not self._is_valid_msg(update):
            return

        if not self.db.child("registros_abertos").get().val():
            return update.message.reply_text("Os registros estão fechados.")

        return update.message.reply_text(self._get_lista_presenca())


    def uuid(self, bot, update):
        user = update.message.from_user.to_dict()

        self.db.child("users").child(user["id"]).set(user)

        text = "{} {}: {}".format(user["first_name"], user["last_name"], user["id"])

        return update.message.reply_text(text)


    def _is_valid_msg(self, update):
        """
        A mensagem é válida se vier do grupo StackOvergol
        """

        user = update.message.from_user.to_dict()

        if user["id"] in self.LISTA_ADMINS:
            logger.info("User is ADMIN, skip validation")
            return True

        if update.message.chat.id == self.GROUP_ID:
            return True

        logger.info("Invalid msg")

        return False


    def _get_lista_presenca(self):
        """Cria o texto da lista de presença"""

        try:
            lista = self.db.child("lista").get().val().values()
        except Exception:
            lista = []

        lista = sorted(lista, key=itemgetter("timestamp"))

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

            todos_goleiros.append("{} - [{}] {} {}".format(
                i + 1,
                user["timestamp"],
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
            todos_jogadores.append("{} - [{}] {} {} (M)".format(
                i + 1,
                user["timestamp"],
                user["first_name"],
                user["last_name"]
            ))


        lp_convidados = [ user for user in lista if user["id"] not in self.LISTA_MENSALISTAS and "goleiro" not in user ]
        for i, user in enumerate(lp_convidados):
            if len(todos_jogadores) == self.MAX_VAGAS_JOGADORES:
                todos_jogadores.append("Lista de Espera:")

            todos_jogadores.append("{} - [{}] {} {} (C)".format(
                i + 1 + len(lp_mensalistas),
                user["timestamp"],
                user["first_name"],
                user["last_name"]
            ))

        linhas.append("Jogadores:")
        if len(todos_jogadores):
            linhas += todos_jogadores
        else:
            linhas.append("----")

        lp_farrapeiros = self.db.child("farrapeiros").get().val()

        if lp_farrapeiros:
            lp_farrapeiros = lp_farrapeiros.values()
        else:
            lp_farrapeiros = []

        if lp_farrapeiros:
            linhas.append("=" * 15)
            linhas.append("Farrapeiros:")

            for i, user in enumerate(lp_farrapeiros):
                linhas.append("{} - [{}] {} {} ({})".format(
                    i + 1,
                    user["timestamp"],
                    user["first_name"],
                    user["last_name"],
                    "M" if user["id"] in self.LISTA_MENSALISTAS else "C"
                ))

        return "\n".join(linhas)

