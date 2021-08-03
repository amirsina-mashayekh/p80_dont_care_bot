#!/usr/bin/python3
# Create module "bot_secrets" and put token of your bot in a variable named "token"
import logging
import os

import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

import data
import handlers
from menuLevels import MenuLevels

logging.basicConfig(
    filename="Log.log", level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main() -> None:
    """Main code"""

    if not (data.connect() and data.create_tables()):
        logging.info('Exiting bot...')
        return

    updater = Updater(token=os.environ.get('BOT_TOKEN'))
    dispatcher = updater.dispatcher

    txt_not_cmd = Filters.text & ~Filters.command

    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='add', callback=handlers.add)],
        states={
            MenuLevels.GET_USER: [MessageHandler(filters=txt_not_cmd, callback=handlers.add_dc)],
            MenuLevels.GET_METHOD: [MessageHandler(filters=txt_not_cmd, callback=handlers.dc_mode)],
            MenuLevels.GET_METHOD_OPTION: [MessageHandler(filters=txt_not_cmd, callback=handlers.dc_mode_option)],
        },
        fallbacks=[
            CommandHandler(command='cancel', callback=handlers.cancel),
            MessageHandler(filters=Filters.reply, callback=handlers.cancel)
        ]
    )

    rem_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='remove', callback=handlers.remove)],
        states={
            MenuLevels.GET_USER: [MessageHandler(filters=txt_not_cmd, callback=handlers.remove_dc)]
        },
        fallbacks=[CommandHandler(command='cancel', callback=handlers.cancel)]
    )

    dispatcher.add_handler(add_conv_handler)
    dispatcher.add_handler(rem_conv_handler)
    dispatcher.add_handler(CommandHandler(command='get_log', callback=handlers.get_log))
    dispatcher.add_handler(CommandHandler(command='del_log', callback=handlers.del_log))
    dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=handlers.message))

    try:
        updater.start_polling()
    except telegram.error.TelegramError:
        logging.exception('Unable to start bot')
        logging.info('Exiting bot...')
        return

    updater.idle()


if __name__ == '__main__':
    main()
