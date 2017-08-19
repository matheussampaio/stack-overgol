import time
import logging

from telegram.ext import Job
from telegram import ParseMode

from models.user import User
from models.group import group

from utils import configs
from database.firebase import database
from decorators.command import Command

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, job_queue):
        group.init(job_queue)

    @Command(onde=False, quando="ABERTO", quem=False)
    def vou(self, bot, update, user):
        if user not in group:
            group.add(user)
            update.message.reply_text("{} adicionado à lista de presença.".format(user))
        else:
            update.message.reply_text("{} já está na lista de presença.".format(user))

    @Command(onde=False, quando="ABERTO", quem=False)
    def vouagarrar(self, bot, update, user):
        if user not in group:
            group.add(user, is_goalkeeper=True)
            update.message.reply_text("{} adicionado à lista de goleiros.".format(user))
        else:
            update.message.reply_text("{} já está na lista de presença.".format(user))

    @Command(onde=False, quando="ABERTO", quem=False)
    def convidado(self, bot, update, user, **kwargs):
        if len(kwargs["args"]) != 3:
            return update.message.reply_text("`/convidado <nome> <sobrenome> <rating>`")

        guest_id = user.id + int(time.time()) - 3 * 60 * 60
        first_name = kwargs["args"][0]
        last_name = kwargs["args"][1]
        rating = float(kwargs["args"][2])

        guest = User(guest_id, first_name, last_name, rating)

        group.add(guest, is_guest=True)
        update.message.reply_text("{} adicionado à lista de convidados.".format(guest))

    @Command(onde=False, quando="ABERTO", quem=False)
    def naovou(self, bot, update, user):
        if user in group:
            group.remove(user)
            update.message.reply_text("{} removido da lista de presença.".format(user))
        else:
            update.message.reply_text("{} não está na lista de presença.".format(user))

    @Command(onde=False, quando=False, quem=False)
    def listar(self, bot, update, user):
        return bot.sendMessage(update.message.chat_id, str(group))

    @Command(onde=False, quando="FECHADO", quem=False)
    def abrir(self, bot, update, user):
        group.open_check_in()
        update.message.reply_text("Registros abertos!")

    @Command(onde=False, quando="ABERTO", quem=False)
    def fechar(self, bot, update, user):
        group.close_check_in()
        update.message.reply_text("Registros fechados!")

    @Command(onde=False, quando=False, quem=False)
    def resetar(self, bot, update, user):
        group.reset()
        update.message.reply_text("Registros resetados!")

    @Command(onde=False, quando=False, quem=False)
    def times(self, bot, update, user):
        bot.send_message(chat_id=update.message.chat_id, text="Calculado times...")

        teams_str = group.calculate_teams()

        bot.send_message(chat_id=update.message.chat_id, text=teams_str, parse_mode=ParseMode.MARKDOWN)
