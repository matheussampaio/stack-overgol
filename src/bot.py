import time
import logging

from datetime import datetime, timedelta
from models.user import User
from models.group import group
from utils.config import Config
from decorators.command import Command
from telegram import ParseMode
import pytz

logger = logging.getLogger(__name__)

def get_next_datetime(date):
    day, hour, timezone = date.split(" ")
    hour, minute = map(int, hour.split(":"))

    temp = datetime.now(pytz.timezone(timezone))

    if temp.hour >= hour and temp.minute >= minute:
      temp += timedelta(days=1)

    temp = temp.replace(hour=hour, minute=minute, second=0, microsecond=0)

    while temp.strftime("%A").lower() != day.lower():
        temp += timedelta(days=1)

    return temp.astimezone(pytz.timezone("UTC")).replace(tzinfo=None)


class Bot:
    def __init__(self, job_queue):
        self.job_queue = job_queue

        group.init(self.job_queue)

        self.schedule_open_check_in()
        self.schedule_close_check_in()

    def schedule_open_check_in(self):
        def open_check_in_callback(bot, job):
            group.reset()
            bot.send_message(chat_id=Config.telegram_group_id(), text="Registros resetados.")

            if not group.is_check_in_open():
                group.open_check_in()
                bot.send_message(chat_id=Config.telegram_group_id(), text="Registros abertos.")

        first_date = get_next_datetime(Config.racha_open_check_in_date())

        return self.job_queue.run_repeating(open_check_in_callback, timedelta(days=7), first=first_date)

    def schedule_close_check_in(self):
        def close_check_in_callback(bot, job):
            if group.is_check_in_open():
                group.close_check_in()
                bot.send_message(chat_id=Config.telegram_group_id(), text="Registros fechados.")

        first_date = get_next_datetime(Config.racha_close_check_in_date())

        return self.job_queue.run_repeating(close_check_in_callback, timedelta(days=7), first=first_date)

    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vou(self, bot, update, user):
        if user not in group:
            group.add(user)
            return update.message.reply_text("{} adicionado à lista de presença.".format(user))

        return update.message.reply_text("{} já está na lista de presença.".format(user))

    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def vouagarrar(self, bot, update, user):
        if user not in group:
            group.add(user, is_goalkeeper=True)

            return update.message.reply_text("{} adicionado à lista de goleiros.".format(user))

        return update.message.reply_text("{} já está na lista de presença.".format(user))

    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def convidado(self, bot, update, user, **kwargs):
        if len(kwargs["args"]) != 3:
            return update.message.reply_text("`/convidado <nome> <sobrenome> <rating>`", parse_mode=ParseMode.MARKDOWN)

        guest_id = user.uid + int(datetime.utcnow().timestamp()) - 3 * 60 * 60
        first_name = kwargs["args"][0]
        last_name = kwargs["args"][1]
        rating = float(kwargs["args"][2])

        if rating < 1:
            rating = 1.0

        guest = User(guest_id, first_name, last_name, rating)

        group.add(guest, is_guest=True)

        return update.message.reply_text("{} adicionado à lista de convidados.".format(guest))

    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def convidado_agarrar(self, bot, update, user, **kwargs):
        if len(kwargs["args"]) != 2:
            return update.message.reply_text("`/convidado_agarrar <nome> <sobrenome>`", parse_mode=ParseMode.MARKDOWN)

        guest_id = user.uid + int(datetime.utcnow().timestamp()) - 3 * 60 * 60
        first_name = kwargs["args"][0]
        last_name = kwargs["args"][1]

        guest = User(guest_id, first_name, last_name)

        group.add(guest, is_goalkeeper=True, is_guest=True)

        return update.message.reply_text("{} adicionado à lista de goleiros.".format(guest))

    @Command(onde="GRUPO", quando="ABERTO", quem=False)
    def naovou(self, bot, update, user):
        if group.remove(user):
            return update.message.reply_text("{} removido da lista de presença.".format(user))

        return update.message.reply_text("{} não está na lista de presença.".format(user))

    @Command(onde=False, quando=False, quem=False)
    def listar(self, bot, update, user, **kwargs):
        show_aditional_info = len(kwargs["args"]) and kwargs["args"][0] == "mais"
        group_list = group.format(show_aditional_info)

        return update.message.reply_text(text=group_list, parse_mode=ParseMode.MARKDOWN)

    @Command(onde=False, quando="FECHADO", quem="ADMIN")
    def abrir(self, bot, update, user):
        group.open_check_in()

        return update.message.reply_text("Registros abertos!")

    @Command(onde=False, quando="ABERTO", quem="ADMIN")
    def fechar(self, bot, update, user):
        group.close_check_in()

        return update.message.reply_text("Registros fechados!")

    @Command(onde=False, quando=False, quem="ADMIN")
    def resetar(self, bot, update, user):
        group.reset()

        return update.message.reply_text("Registros resetados!")

    @Command(onde=False, quando=False, quem="ADMIN")
    def times(self, bot, update, user, **kwargs):
        if len(kwargs["args"]) != 0 and len(kwargs["args"]) != 2:
            return update.message.reply_text(
                text="Use `/times` ou `/times <number_teams> <team_size>`.",
                parse_mode=ParseMode.MARKDOWN
            )

        number_teams = Config.racha_max_teams()
        team_size = Config.racha_max_number_players_team()

        if len(kwargs["args"]) == 2:
            number_teams = int(kwargs["args"][0])
            team_size = int(kwargs["args"][1])

        teams_str = group.calculate_teams(
            number_teams,
            team_size,
            team_colors=Config.racha_teams_colors(),
            rating_range_variation=[Config.racha_rating_range_variation_min(), Config.racha_rating_range_variation_max()],
            complete_team_with_fake_players=Config.racha_complete_teams_with_fake_players(),
            with_substitutes=Config.racha_has_substitutes_list()
        )

        return update.message.reply_text(text=teams_str, parse_mode=ParseMode.MARKDOWN)

    @Command(onde=False, quando=False, quem="ADMIN")
    def load(self, bot, update, user):
        group.load()

        return update.message.reply_text("Carregando dados...")

    @Command(onde=False, quando=False, quem="ADMIN")
    def save(self, bot, update, user):
        group.save()

        return update.message.reply_text("Salvando dados...")

    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def naovai(self, bot, update, user, **kwargs):
        if not kwargs["args"]:
            return update.message.reply_text("`/naovai <nome> <sobrenome>` or `/naovai <uid>`", parse_mode=ParseMode.MARKDOWN)

        term = " ".join(kwargs["args"])

        if term.isdigit():
            listitems = group.find_on_list_with_uid(int(term))
        else:
            listitems = group.find_on_list(term)

        if not listitems and term.isdigit():
            return update.message.reply_text("Não consigo achar nenhum jogador com UID `{}`".format(term), parse_mode=ParseMode.MARKDOWN)

        if not listitems:
            return update.message.reply_text("Não consigo achar nenhum jogador com '{}'".format(term))

        if len(listitems) > 1:
            output = "Vários jogadores encontrados, tente filtrar um pouco mais:\n"

            for i, listitem in enumerate(sorted(listitems, key=lambda listitem: listitem.user.full_name)):
                output += " - {} (`{}`)\n".format(listitem, listitem.user.uid)

            return update.message.reply_text(output, parse_mode=ParseMode.MARKDOWN)

        if group.remove(listitems[0].user):
            return update.message.reply_text("{} removido da lista de presença.".format(listitems[0]))

        return update.message.reply_text("Error: {}.".format(listitems[0]))

    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def vai(self, bot, update, user, **kwargs):
        if not kwargs["args"]:
            return update.message.reply_text("`/vai <nome> <sobrenome>` or `/vai <uid>`", parse_mode=ParseMode.MARKDOWN)

        term = " ".join(kwargs["args"])

        if term.isdigit():
            players = group.find_on_all_players_with_uid(int(term), filter_players_on_list=True)
        else:
            players = group.find_on_all_players(term, filter_players_on_list=True)

        logger.info(players)

        if not players and term.isdigit():
            return update.message.reply_text("Não consigo achar nenhum jogador com UID `{}`".format(term), parse_mode=ParseMode.MARKDOWN)

        if not players:
            return update.message.reply_text("Não consigo achar nenhum jogador com '{}'".format(term))

        if len(players) > 1:
            output = "Vários jogadores encontrados, tente filtrar um pouco mais:\n"

            for i, player in enumerate(sorted(players, key=lambda player: player.full_name)):
                output += " - {} (`{}`)\n".format(player, player.uid)

            return update.message.reply_text(output, parse_mode=ParseMode.MARKDOWN)

        if group.add(players[0], is_guest=players[0].is_guest):
            return update.message.reply_text("{} adicionado na lista de presença.".format(players[0]))

        return update.message.reply_text("Error: {}".format(players[0]))

    @Command(onde="GRUPO", quando=False, quem="ADMIN")
    def vai_agarrar(self, bot, update, user, **kwargs):
        term = ""

        if kwargs["args"]:
            term = " ".join(kwargs["args"])

        players = group.find_on_all_players(term, filter_players_on_list=True)

        if not players:
            return update.message.reply_text("Não consigo achar nenhum jogador com '{}'".format(term))

        if len(players) > 1:
            output = "Vários jogadores encontrados, tente filtrar um pouco mais:\n"

            for i, player in enumerate(sorted(players, key=lambda p: p.full_name)):
                output += " - {}\n".format(player)

            return update.message.reply_text(output)

        if group.add(players[0], is_goalkeeper=True, is_guest=players[0].is_guest):
            return update.message.reply_text("{} adicionado na lista de goleiros.".format(players[0]))

        return update.message.reply_text("Error: {}".format(players[0]))

    @Command(onde=False, quando=False, quem=False)
    def timestamp(self, bot, update, user, **kwargs):
        return update.message.reply_text("Datetime: {}".format(datetime.utcnow().isoformat()))
