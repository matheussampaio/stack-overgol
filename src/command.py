import time
import logging

logger = logging.getLogger(__name__)

class Command(object):
    def __init__(self, onde="GRUPO", quando="ABERTO", quem=False):
        self.onde = onde
        self.quando = quando
        self.quem = quem

    def __call__(self, f):

        def wrapper_f(_self, bot, update, *args, **kwargs):
            user = update.message.from_user.to_dict()

            del user["type"]

            group_id = update.message.chat.id

            group_value = _self.db.child("groups").child(group_id).get().val()

            _self.db.child("users").child(user["id"]).update(user)

            user["is_admin"] = bool(str(user["id"]) in group_value["admins"])
            user["is_mensalista"] = bool(str(user["id"]) in group_value["mensalistas"])

            # ONDE: "GRUPO", False
            if self.onde == "GRUPO" and not group_value:
                return update.message.reply_text("Esse comando só é válido dentro do grupo.")

            # QUEM: "ADMIN", "MENSALISTA", False
            if self.quem == "ADMIN" and not user["is_admin"]:
                return update.message.reply_text("Comando restrito à admins.")

            if self.quem == "MENSALISTA" and not (user["is_mensalista"] or user["is_admin"]):
                return update.message.reply_text("Comando restrito à mensalistas.")

            # QUANDO: "ABERTO", "FECHADO", False
            if self.quando == "ABERTO" and not group_value["registros_abertos"]:
                return update.message.reply_text("Esse comando não pode ser usado com os registros fechados.")

            hora_de_abrir = group_value["hora_abrir_registros"]
            epoch_abrir = time.mktime(time.strptime(hora_de_abrir, "%H:%Mh %d/%m/%y"))

            if self.quando == "ABERTO" and group_value["registros_abertos"] \
                and int(update.message.date.strftime("%s")) < epoch_abrir:
                return update.message.reply_text("Comando enviado antes de abrir.")

            if self.quando == "FECHADO" and group_value["registros_abertos"]:
                return update.message.reply_text("Esse comando não pode ser usado com os registros abertos.")

            f(_self, bot, update, user, group_id, *args, **kwargs)

        return wrapper_f
