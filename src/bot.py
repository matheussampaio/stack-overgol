import time
import logging

# from telegram.ext import Job

from models.user import User
from models.group import Group

from decorators.command import Command
from database.firebase import database

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self, job_queue):
        self.job_queue = job_queue
        self.group = Group()

        self.schedule_open_check_in()
        self.schedule_close_check_in()

    @Command(onde=False, quando="ABERTO", quem=False)
    def vou(self, bot, update, user):
        if user not in self.group:
            self.group.add(user)
            update.message.reply_text("{} adicionado à lista de presença.".format(user))
        else:
            update.message.reply_text("{} já está na lista de presença.".format(user))

    @Command(onde=False, quando="ABERTO", quem=False)
    def vouagarrar(self, bot, update, user):
        if user not in self.group:
            self.group.add(user, is_goalkeeper=True)
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

        self.group.add(guest, is_guest=True)
        update.message.reply_text("{} adicionado à lista de convidados.".format(guest))

    @Command(onde=False, quando="ABERTO", quem=False)
    def naovou(self, bot, update, user):
        if user in self.group:
            self.group.remove(user)
            update.message.reply_text("{} removido da lista de presença.".format(user))
        else:
            update.message.reply_text("{} não está na lista de presença.".format(user))

    @Command(onde=False, quando=False, quem=False)
    def listar(self, bot, update, user):
        return bot.sendMessage(update.message.chat_id, str(self.group))

    @Command(onde=False, quando="FECHADO", quem=False)
    def abrir(self, bot, update, user):
        self.group.open_check_in()
        update.message.reply_text("Registros abertos!")

    @Command(onde=False, quando="ABERTO", quem=False)
    def fechar(self, bot, update, user):
        self.group.close_check_in()
        update.message.reply_text("Registros fechados!")

    @Command(onde=False, quando=False, quem=False)
    def resetar(self, bot, update, user):
        self.group.reset()
        update.message.reply_text("Registros resetados!")

    def schedule_open_check_in(self):
        pass
        # def callback_open_check_in(bot, job):
        #     bot.send_message(chat_id="227260861", text='One message every minute')
        #
        # job_minute = Job(callback_open_check_in, 60.0)
        #
        # self.job_queue.put(job_minute, next_t=0.0)

    def schedule_close_check_in(self):
        pass
