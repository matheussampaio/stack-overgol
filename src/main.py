#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sentry_sdk

from utils.config import Config

if Config.sentry():
    sentry_sdk.init(Config.sentry())

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=Config.log_level())

logger = logging.getLogger(__name__)

# from stack_overgol import StackOvergol
from bot import Bot


def error(bot, update, err):
    logger.error('Update "%s" caused error "%s"', update, err)


def main():
    updater = Updater(Config.telegram_token())

    STACK_OVERGOL_CORE = Bot(updater.job_queue)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # ADMIN
    dp.add_handler(CommandHandler("abrir", STACK_OVERGOL_CORE.abrir))
    dp.add_handler(CommandHandler("convidado", STACK_OVERGOL_CORE.convidado, pass_args=True))
    dp.add_handler(CommandHandler("convidado_agarrar", STACK_OVERGOL_CORE.convidado_agarrar, pass_args=True))
    dp.add_handler(CommandHandler("fechar", STACK_OVERGOL_CORE.fechar))
    dp.add_handler(CommandHandler("load", STACK_OVERGOL_CORE.load))
    dp.add_handler(CommandHandler("naovai", STACK_OVERGOL_CORE.naovai, pass_args=True))
    dp.add_handler(CommandHandler("resetar", STACK_OVERGOL_CORE.resetar))
    dp.add_handler(CommandHandler("save", STACK_OVERGOL_CORE.save))
    dp.add_handler(CommandHandler("times", STACK_OVERGOL_CORE.times, pass_args=True))
    dp.add_handler(CommandHandler("vai", STACK_OVERGOL_CORE.vai, pass_args=True))
    dp.add_handler(CommandHandler("vai_agarrar", STACK_OVERGOL_CORE.vai_agarrar, pass_args=True))

    # ALL
    dp.add_handler(CommandHandler("listar", STACK_OVERGOL_CORE.listar, pass_args=True))
    dp.add_handler(CommandHandler("naovou", STACK_OVERGOL_CORE.naovou))
    dp.add_handler(CommandHandler("vou", STACK_OVERGOL_CORE.vou))
    dp.add_handler(CommandHandler("vouagarrar", STACK_OVERGOL_CORE.vouagarrar))
    dp.add_handler(CommandHandler("timestamp", STACK_OVERGOL_CORE.timestamp))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
