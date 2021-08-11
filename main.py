#!/usr/bin/python3

# To test bot locally:
# - Create a new module (e.g. local_start.py)
# - Import main
# - Define BOT_TOKEN, OWNER_ID and DATABASE_URL environment variables as strings (os.environ['key'] = 'val')
# - Call main.main()
# - Run that module

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
    level=logging.INFO, format='%(asctime)s, %(name)s, %(levelname)s: %(message)s'
)


def main() -> None:
    """Main code"""

    if not (data.connect() and data.create_tables()):
        logging.info('Exiting bot...')
        return

    bot_token = os.environ.get('BOT_TOKEN')
    updater = Updater(token=bot_token)
    dispatcher = updater.dispatcher

    txt_not_cmd = Filters.text & ~Filters.command
    msg_filter = Filters.all & ~(Filters.game | Filters.poll | Filters.status_update)

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

    rem_all_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='remove_all', callback=handlers.remove_all)],
        states={
            0: [MessageHandler(filters=txt_not_cmd, callback=handlers.remove_all_confirm)]
        },
        fallbacks=[CommandHandler(command='cancel', callback=handlers.cancel)]
    )

    dispatcher.add_handler(add_conv_handler)
    dispatcher.add_handler(rem_conv_handler)
    dispatcher.add_handler(rem_all_conv_handler)
    dispatcher.add_handler(MessageHandler(filters=msg_filter, callback=handlers.message))

    try:
        if os.environ.get('DATABASE_URL').__contains__('localhost'):
            # Local test
            updater.start_polling()
        else:
            # Web app
            updater.start_webhook(listen='0.0.0.0', port=int(os.environ.get('PORT', 5000)), url_path=bot_token,
                                  webhook_url='https://p80-dont-care-bot.herokuapp.com/' + bot_token)
    except telegram.error.TelegramError:
        logging.exception('Unable to start bot')
        logging.info('Exiting bot...')
        return

    updater.idle()


if __name__ == '__main__':
    main()
