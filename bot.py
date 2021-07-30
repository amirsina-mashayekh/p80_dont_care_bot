#!/usr/bin/python3
#Create module "bot_tokey" and put token of your bot in a variable named "token" 
import bot_token, handlers
from menuLevels import MenuLevels
import logging
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler
)

logging.basicConfig(
    filename="Log.log", level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main() -> None:
    "Main code"

    updater = Updater(token=bot_token.token)
    dispatcher = updater.dispatcher

    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='add', callback=handlers.add)],
        states={
            MenuLevels.GET_USER: [MessageHandler(filters=Filters.reply, callback=handlers.addDC)],
            MenuLevels.GET_METHOD: [MessageHandler(filters=Filters.reply, callback=handlers.dcMode)],
            MenuLevels.GET_METHOD_OPTION: [MessageHandler(filters=Filters.reply, callback=handlers.dcModeOption)],
        },
        fallbacks=[
            CommandHandler(command='cancel', callback=handlers.cancel),
            MessageHandler(filters=Filters.reply, callback=handlers.cancel)
        ]
    )

    rem_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='remove', callback=handlers.remove)],
        states={
            MenuLevels.GET_USER: [MessageHandler(filters=Filters.reply, callback=handlers.removeDC)]
        },
        fallbacks=[CommandHandler(command='cancel', callback=handlers.cancel)]
    )

    dispatcher.add_handler(add_conv_handler)
    dispatcher.add_handler(rem_conv_handler)
    dispatcher.add_handler(MessageHandler(filters=Filters.all, callback=handlers.message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()