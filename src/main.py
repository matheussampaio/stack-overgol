#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
# import sys
import logging

from utils import configs

os.environ["TZ"] = configs.get("TIMEZONE")

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO if configs.get("DEBUG") else logging.INFO)

logger = logging.getLogger(__name__)

# from stack_overgol import StackOvergol
from bot import Bot


def error(bot, update, err):
    logger.warn('Update "%s" caused error "%s"', update, err)


def main():
    updater = Updater(configs.get("TELEGRAM.TOKEN"))

    STACK_OVERGOL_CORE = Bot(updater.job_queue)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # ADMIN
    dp.add_handler(CommandHandler("convidado", STACK_OVERGOL_CORE.convidado, pass_args=True))
    dp.add_handler(CommandHandler("abrir", STACK_OVERGOL_CORE.abrir))
    dp.add_handler(CommandHandler("fechar", STACK_OVERGOL_CORE.fechar))
    dp.add_handler(CommandHandler("resetar", STACK_OVERGOL_CORE.resetar))
    # dp.add_handler(CommandHandler("vai", STACK_OVERGOL_CORE.vai))
    # dp.add_handler(CommandHandler("adicionar_mensalista", STACK_OVERGOL_CORE.adicionar_mensalista))
    # dp.add_handler(CommandHandler("remover_mensalista", STACK_OVERGOL_CORE.remover_mensalista))
    # dp.add_handler(CommandHandler("mensalistas", STACK_OVERGOL_CORE.mensalistas))
    # dp.add_handler(CommandHandler("naovai", STACK_OVERGOL_CORE.nao_vai))
    dp.add_handler(CommandHandler("times", STACK_OVERGOL_CORE.times))

    # ALL
    dp.add_handler(CommandHandler("vou", STACK_OVERGOL_CORE.vou))
    dp.add_handler(CommandHandler("vouagarrar", STACK_OVERGOL_CORE.vouagarrar))
    dp.add_handler(CommandHandler("naovou", STACK_OVERGOL_CORE.naovou))
    dp.add_handler(CommandHandler("listar", STACK_OVERGOL_CORE.listar))

    # OTHERS
    # dp.add_handler(CallbackQueryHandler(STACK_OVERGOL_CORE.vai_nao_vai_callback))

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
