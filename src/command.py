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

            _self.db.child("users").child(user["id"]).set(user)

            # ONDE: "GRUPO", False

            if self.onde == "GRUPO" and update.message.chat.id != _self.GROUP_ID and user["id"] not in _self.LISTA_ADMINS:
                return update.message.reply_text("Esse comando só é válido dentro do grupo.")

            # QUEM: "ADMIN", "MENSALISTA", False

            if self.quem == "ADMIN" and user["id"] not in _self.LISTA_ADMINS:
                return update.message.reply_text("Comando restrito à admins.")

            if self.quem == "MENSALISTA" and user["id"] not in _self.LISTA_MENSALISTAS + _self.LISTA_ADMINS:
                return update.message.reply_text("Comando restrito à mensalistas.")

            # QUANDO: "ABERTO", "FECHADO", False

            try:
                registros_abertos = _self.db.child("registros_abertos").get().val()
            except AttributeError:
                registros_abertos = False

            if self.quando == "ABERTO" and not registros_abertos:
                return update.message.reply_text("Esse comando não pode ser usado com os registros fechados.")

            if self.quando == "FECHADO" and registros_abertos:
                return update.message.reply_text("Esse comando não pode ser usado com os registros abertos.")

            f(_self, bot, update, user, *args, **kwargs)

        return wrapper_f
