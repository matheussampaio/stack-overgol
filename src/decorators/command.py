import time

from models.group import group
from utils.config import Config

class Command(object):
    def __init__(self, onde="GRUPO", quando="ABERTO", quem=False):
        self.onde = onde
        self.quando = quando
        self.quem = quem

    def __call__(self, f):
        def wrapper_f(_self, bot, update, *args, **kwargs):
            data = update.message.from_user.to_dict()

            user = group.get_user_or_create(data)

            user.last_seen = time.time()
            group.should_sync = True

            # Sempre permitir mensagens vindas do Master Admin
            if user.uid in Config.master_admin_telegram_id():
                return f(_self, bot, update, user, *args, **kwargs)

            # ONDE: "GRUPO", False
            if self.onde == "GRUPO" and update.message.chat.id != int(Config.telegram_group_id()):
                return update.message.reply_text("Esse comando só é válido dentro do grupo.")

            # QUEM: "ADMIN", "MENSALISTA", False
            if self.quem == "ADMIN" and not user.is_admin:
                return update.message.reply_text("Comando restrito à admins.")

            if self.quem == "MENSALISTA" and not user.is_subscriber:
                return update.message.reply_text("Comando restrito à mensalistas.")

            # QUANDO: "ABERTO", "FECHADO", False
            if self.quando == "ABERTO" and not group.is_check_in_open():
                return update.message.reply_text("Esse comando não pode ser usado com os registros fechados.")

            # TODO: Verificar se o comando foi enviado um pouco antes do check-in abrir, porém o bot só
            #       processou o comando após alguns segundos.
            #
            # hora_de_abrir = group_value["hora_abrir_registros"]
            # epoch_abrir = time.mktime(time.strptime(hora_de_abrir, "%H:%Mh %d/%m/%y"))
            #
            # if self.quando == "ABERTO" and group_value["registros_abertos"] \
            #     and int(update.message.date.strftime("%s")) < epoch_abrir:
            #     return update.message.reply_text("Comando enviado antes de abrir.")

            if self.quando == "FECHADO" and group.is_check_in_open():
                return update.message.reply_text("Esse comando não pode ser usado com os registros abertos.")

            return f(_self, bot, update, user, *args, **kwargs)

        return wrapper_f
