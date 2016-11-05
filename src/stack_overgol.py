# -*- coding: utf-8 -*-

import time
import logging
from operator import itemgetter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import configs
from usuarios import Usuarios

logger = logging.getLogger(__name__)

class StackOvergol:

    def __init__(self):
        self.lp_mensalistas = []
        self.lp_convidados = []
        self.lp_convidados_de_alguem = []
        self.lp_goleiros = []
        self.lp_farrapeiros = []

        self.usuarios = Usuarios()
        self.registros_abertos = configs.DEBUG or False


    def vai(self, bot, update):
        """
        @Comando: /vai
        @Quem: A

        Quando o admin enviar o comando, o bot deve mostrar a lista de usuários
        que não estão na lista de presença. O usuário deve selecionar um dentre
        as opções. O bot deve colocar o usuário selecionado na lista de
        presença.
        """

        user = update.message.from_user

        self._save_user(user)

        if not user["id"] in configs.LISTA_ADMINS:
            return

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            update.message.reply_text("Os registros estão fechados.")
            return

        keyboard = []

        logger.info(configs.LISTA_MENSALISTAS)

        # Só mostrar os usuários que ainda não estão na lista de presença e são mensalistas
        usuarios = [user for user in self.usuarios.values() if user["id"] in configs.LISTA_MENSALISTAS]

        usuarios = sorted(usuarios, key=itemgetter("first_name", "last_name"))

        if len(usuarios):
            for user in usuarios:
                keyboard.append([InlineKeyboardButton("{} {}".format(user["first_name"], user["last_name"]), callback_data=str(user["id"]))])

            keyboard.append([InlineKeyboardButton("Cancelar", callback_data="-1")])

            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Quem vai?", reply_markup=reply_markup)

        else:
            update.message.reply_text("Ninguém disponivel.")


    def nao_vai(self, bot, update):
        """
        @Comando: /naovai
        @Quem: A

        Quando o adimin enviar o comando, o bot irá mostrar a lista de usuários
        que estão na lista de presença. O usuário deverá escolher um dentre as
        opções. O bot deve retirar o usuário selecionado da lista de presença.
        """
        user = update.message.from_user

        self._save_user(user)

        if not user["id"] in configs.LISTA_ADMINS:
            return

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            update.message.reply_text("Os registros estão fechados.")
            return

        keyboard = []

        usuarios = self.lp_goleiros + self.lp_mensalistas + self.lp_convidados

        if not len(usuarios):
            update.message.reply_text("Lista de presença vazia.")
            return

        for user in usuarios:
            user_name = "{} {}".format(user["first_name"], user["last_name"])
            keyboard.append([
                InlineKeyboardButton(user_name, callback_data=str(user["id"]))
                ])

        keyboard.append([InlineKeyboardButton("Cancelar", callback_data="-1")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Quem nao vai?", reply_markup=reply_markup)


    def vai_nao_vai_callback(self, bot, update):
        query = update.callback_query
        query_dict = query.to_dict()

        text = query_dict["message"]["text"]

        from_user = query_dict["from"]

        if not from_user["id"] in configs.LISTA_ADMINS:
            return

        data = query_dict["data"]

        if data == "-1":
            return bot.editMessageText(text="Cancelado",
                                       chat_id=query.message.chat_id,
                                       message_id=query.message.message_id)

        user = self.usuarios.get(data)
        if not user:
            message = "Nenhum usuário com id: {}".format(data)

        elif text == "Quem vai?":
            if self._adiciona_lista(user):
                self.lp_farrapeiros = [tUser for tUser in self.lp_farrapeiros if tUser["id"] != user["id"]]

                message = "{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"])
            else:
                message = "{} {} já está na lista.".format(user["first_name"], user["last_name"])
        else:
            if self._remove_listas(user):
                if not self._is_user_in_lista(user, self.lp_farrapeiros):
                    try:
                        user["timestamp"] = time.strftime("%X")
                    except:
                        user.timestamp = time.strftime("%X")

                    self.lp_farrapeiros.append(user)

                message = "{} {} removido da lista de presença.".format(user["first_name"], user["last_name"])
            else:
                message = "{} {} não está na lista.".format(user["first_name"], user["last_name"])

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

        self._save_user(update.message.from_user)

        if not self._is_valid_msg(update):
            return

        if self.registros_abertos:
            update.message.reply_text("Os registros já estão abertos.")
            return

        id_usuario = update.message.from_user.id

        if id_usuario in configs.LISTA_ADMINS and not self.registros_abertos:
            self.lp_mensalistas = []
            self.lp_convidados = []
            self.lp_convidados_de_alguem = []
            self.lp_goleiros = []
            self.lp_farrapeiros = []
            self.registros_abertos = True

            update.message.reply_text("Registros abertos!")


    def terminar(self, bot, update):
        """
        @Comando: /terminar
        @Quem: A

        Quando o admin enviar o comando, os registros serão encerrados e a
        lista final é impressa.

        @TODO: Deve definir os times.
        @TODO: Deve sortear a ordem dos times (quem joga primeiro).
        """

        self._save_user(update.message.from_user)

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            update.message.reply_text("Os registros estão fechados.")
            return

        id_usuario = update.message.from_user.id

        if id_usuario in configs.LISTA_ADMINS:
            self.registros_abertos = False

            lista_final = self._get_lista_presenca()

            text = "Registro encerrado!\n\nLISTA FINAL:\n{}".format(lista_final)

            update.message.reply_text(text)


    def vou_agarrar(self, bot, update):
        """
        @Comando: /vouagarrar
        @Quem: M, C

        Quando o usuário enviar o comando, se não estiver em nenhuma lista,
        adiciona o usuário na lista de goleiros.
        """

        user = update.message.from_user

        self._save_user(user)

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            update.message.reply_text("Os registros estão fechados.")
            return

        self.lp_farrapeiros = [tUser for tUser in self.lp_farrapeiros if tUser["id"] != user["id"]]

        if self._adiciona_lista_agarrar(user):
            update.message.reply_text("{} {} adicionado à lista de goleiros.".format(user["first_name"], user["last_name"]))
        else:
            update.message.reply_text("{} {} já está na lista.".format(user["first_name"], user["last_name"]))


    def vou(self, bot, update):
        """
        @Comando: /vou
        @Quem: M, C

        Quando o usúario digitar o comando, se não estiver em nenhuma lista,
        será adicionado.
        """

        user = update.message.from_user

        self._save_user(user)

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            update.message.reply_text("Os registros estão fechados.")
            return

        self.lp_farrapeiros = [tUser for tUser in self.lp_farrapeiros if tUser["id"] != user["id"]]

        if self._adiciona_lista(user):
            update.message.reply_text("{} {} adicionado à lista de presença.".format(user["first_name"], user["last_name"]))
        else:
            update.message.reply_text("{} {} já está na lista.".format(user["first_name"], user["last_name"]))


    def naovou(self, bot, update):
        """
        @Comando: /naovou
        @Quem: Mensalistas, Goleiros e Convidados

        Quando o usuário enviar o comando, será removido da lista
        correspondente.
        """

        user = update.message.from_user

        self._save_user(user)

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            update.message.reply_text("Os registros estão fechados.")
            return

        self._remove_listas(user)

        if not self._is_user_in_lista(user, self.lp_farrapeiros):
            try:
                user["timestamp"] = time.strftime("%X")
            except:
                user.timestamp = time.strftime("%X")

            self.lp_farrapeiros.append(user)

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

        self._save_user(update.message.from_user)

        if not self._is_valid_msg(update):
            return

        if not self.registros_abertos:
            return

        self._imprimir_lista_presenca(update)


    def uuid(self, bot, update):
        self._save_user(update.message.from_user)

        if not self._is_valid_msg(update):
            return

        user = update.message.from_user

        text = "{} {}: {}".format(user["first_name"], user["last_name"], user["id"])

        return update.message.reply_text(text)


    def _adiciona_lista_agarrar(self, user):
        if not self._is_in_any_lista(user):
            user.timestamp = time.strftime("%X")
            self.lp_goleiros.append(user)
            return True

        return False


    def _adiciona_lista(self, user):
        if not self._is_in_any_lista(user):
            try:
                user["timestamp"] = time.strftime("%X")
            except:
                user.timestamp = time.strftime("%X")

            if user["id"] in configs.LISTA_MENSALISTAS:
                self.lp_mensalistas.append(user)
            else:
                self.lp_convidados.append(user)

            return True

        return False


    def _remove_listas(self, user):
        old_len_lpm = len(self.lp_mensalistas)
        self.lp_mensalistas = [tUser for tUser in self.lp_mensalistas if tUser["id"] != user["id"]]

        old_len_lpc = len(self.lp_convidados)
        self.lp_convidados = [tUser for tUser in self.lp_convidados if tUser["id"] != user["id"]]

        old_len_lpg = len(self.lp_goleiros)
        self.lp_goleiros = [tUser for tUser in self.lp_goleiros if tUser["id"] != user["id"]]

        if old_len_lpm != len(self.lp_mensalistas) \
                or old_len_lpc != len(self.lp_convidados) \
                or old_len_lpg != len(self.lp_goleiros):
            return True

        return False


    def _is_in_any_lista(self, user):
        is_in_lista_M = self._is_user_in_lista(user, self.lp_mensalistas)
        is_in_lista_C = self._is_user_in_lista(user, self.lp_convidados)
        is_in_lista_G = self._is_user_in_lista(user, self.lp_goleiros)

        return is_in_lista_M or is_in_lista_C or is_in_lista_G


    def _is_user_in_lista(self, user, lista):
        for tmp_user in lista:
            if tmp_user["id"] == user["id"]:
                return True

        return False


    def _imprimir_lista_presenca(self, update):
        """Imprimi a lista de presença atual"""

        return update.message.reply_text(self._get_lista_presenca())


    def _is_valid_msg(self, update):
        """
        A mensagem é válida se vier do grupo StackOvergol
        """

        user = update.message.from_user

        if user["id"] in configs.LISTA_ADMINS:
            logger.info("User is ADMIN, skip validation")
            return True

        if configs.DEBUG:
            logger.info("DEBUG mode, skip validation")
            return True

        if update.message.chat.id == configs.GROUP_ID:
            return True

        return False


    def _save_user(self, user):
        self.usuarios.add(user)


    def _get_lista_presenca(self):
        """Cria o texto da lista de presença"""

        # Adiciona o cabecalho
        linhas = [
            "Lista de Presença",
            "=" * 15
            ]

        # GOLEIROS
        todos_goleiros = []

        for i, user in enumerate(self.lp_goleiros):
            if len(self.lp_goleiros) == configs.MAX_VAGAS_GOLEIROS:
                todos_goleiros.append("Lista de Espera (Goleiro):")

            todos_goleiros.append("{} - [{}] {} {}".format(
                i + 1,
                user.timestamp,
                user.first_name,
                user.last_name
            ))

        linhas.append("Goleiros:")
        if len(todos_goleiros):
            linhas += todos_goleiros
        else:
            linhas.append("----")
        linhas.append("=" * 15)


        # JOGADORES
        todos_jogadores = []

        for i, user in enumerate(self.lp_mensalistas):
            todos_jogadores.append("{} - [{}] {} {} (M)".format(
                i + 1,
                user["timestamp"],
                user["first_name"],
                user["last_name"]
            ))

        for i, user in enumerate(self.lp_convidados):
            if len(todos_jogadores) == configs.MAX_VAGAS_JOGADORES:
                todos_jogadores.append("Lista de Espera:")

            todos_jogadores.append("{} - [{}] {} {} (C)".format(
                i + 1 + len(self.lp_mensalistas),
                user.timestamp,
                user.first_name,
                user.last_name
            ))

        linhas.append("Jogadores:")
        if len(todos_jogadores):
            linhas += todos_jogadores
        else:
            linhas.append("----")

        if len(self.lp_farrapeiros):
            linhas.append("=" * 15)
            linhas.append("Farrapeiros:")

            for i, user in enumerate(self.lp_farrapeiros):
                linhas.append("{} - [{}] {} {} ({})".format(
                    i + 1,
                    user["timestamp"],
                    user["first_name"],
                    user["last_name"],
                    "M" if user["id"] in configs.LISTA_MENSALISTAS else "C"
                ))

        return "\n".join(linhas)
