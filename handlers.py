from doesntCare import DoesntCare
from menuLevels import MenuLevels
import re, datetime, logging
from telegram import Update, messageentity, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    CallbackContext
)

methodkbd = [
    ['Each time user sends a message!'],
    ['When user sends message after a certain amount of time.'],
    ['After user sent a certain count of messages.'],
    ['Cancel']
]

def createDC(update: Update) -> DoesntCare:
    "Create new DoesntCare from message"
    senderID = update.effective_user.id
    chatID = update.effective_chat.id

    mentions = update.message.parse_entities(messageentity.MessageEntity.TEXT_MENTION)
    try:
        mention = list(mentions.keys())[0]
    except:
        return None

    if mention.type == 'text_mention':
        mentionedID = mention.user.id
    else:
        mentionedID = mentions[mention][1:]

    return DoesntCare(chatID=chatID, notImportantID=mentionedID, doesntCareID=senderID)



def add(update: Update, contex: CallbackContext) -> int:
    "Handle add command"
    update.message.reply_text(
        "Please mention the user who you don't care about in reply of this message. Send /cancel to cancel."
    )
    return MenuLevels.GET_USER



def addDC(update: Update, contex: CallbackContext) -> int:
    "Add a new don't care"
    ndc = createDC(update)

    if ndc == None:
        update.effective_message.reply_text("There is no mention in your message, please try again.")
        return None

    for dc in DoesntCare.dcList:
        if dc == ndc:
            update.effective_message.reply_text("You already don't care about this user!")
            logging.info(
                "Duplicate: DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\""
                .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID)
            )
            return ConversationHandler.END

    contex.user_data[0] = ndc
    rkm = ReplyKeyboardMarkup(methodkbd, one_time_keyboard=True, selective=True, input_field_placeholder='Select one...')

    update.effective_message.reply_text(
        "How often do you want to remind the user that you don't care about him/her?",
        reply_markup=rkm
    )
    return MenuLevels.GET_METHOD



def dcMode(update: Update, contex: CallbackContext) -> int:
    "Get don't care response mode"
    ndc = contex.user_data[0]

    if update.effective_message.text == methodkbd[0][0]:
        ndc.responseMode = DoesntCare.ResponseMode.INSTANT
        if ndc.add():
            rep = "Added user to your don't care list!"
            logging.info(
                "Add: DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\" - RM: \"{}\" - RMO: \"{}\""
                .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID, ndc.responseMode, ndc.responseModeOption)
            )
        else:
            rep = "Sorry, an error occurred! Please try again later."
            logging.error(
                "Add - DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\""
                .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID)
            )
        update.effective_message.reply_text(rep, reply_markup=ReplyKeyboardRemove(selective=True))
        return ConversationHandler.END
    
    elif update.effective_message.text == methodkbd[1][0]:
        ndc.responseMode = DoesntCare.ResponseMode.TIME
        rep = ("Please reply the minimum time before reminding user again in the following format: Hours:Minutes:Seconds\n" + 
            "for example 1:30:0")

    elif update.effective_message.text == methodkbd[2][0]:
        ndc.responseMode = DoesntCare.ResponseMode.MESSAGE_COUNT
        rep = "Please reply the count of messages before reminding user again."    
    else:
        rep = "Invalid answer. Please select one of available options."
        return None
    
    update.effective_message.reply_text(rep, reply_markup=ReplyKeyboardRemove(selective=True))

    contex.user_data[0] = ndc
    return MenuLevels.GET_METHOD_OPTION



def dcModeOption(update: Update, contex: CallbackContext) -> int:
    "Get don't care response mode option"
    ndc = contex.user_data[0]
    
    if ndc.responseMode == DoesntCare.ResponseMode.TIME:
        if not re.match(r"[0-9]+:[0-9]+:[0-9]+", update.effective_message.text):
            update.effective_message.reply_text('Invalid time format, please reply in this format: Hours:Minutes:Seconds')
            return None

        hms = update.effective_message.text.split(':')
        ndc.responseModeOption = datetime.timedelta(hours=int(hms[0]), minutes=int(hms[1]), seconds=int(hms[2]))
    
    else:
        if ((not update.effective_message.text.isdigit()) or
           (not (int(update.effective_message.text) > 1))):
            update.effective_message.reply_text('Invalid number. Please reply a positive integer more than 1.')
            return None

        ndc.responseModeOption = int(update.effective_message.text)

    # Recreate a DoesntCare dc to set counter correctly
    try:
        dc = DoesntCare(ndc.chatID, ndc.notImportantID, ndc.doesntCareID, ndc.responseMode, ndc.responseModeOption)
    except:
        update.effective_message.reply_text("Sorry, something went wrong! Please try again later.")
        logging.exception(
            "New: \"{}\" - NIU: \"{}\" - Chat: \"{}\" - RM: \"{}\" - RMO: \"{}\" - RC: \"{}\""
            .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID, ndc.responseMode, ndc.responseModeOption, ndc.responseCounter)
        )
        return ConversationHandler.END
    if dc.add():
        update.effective_message.reply_text("Added user to your don't care list!")
        logging.info(
            "Add: DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\" - RM: \"{}\" - RMO: \"{}\""
            .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID, ndc.responseMode, ndc.responseModeOption)
        )
    else:
        update.effective_message.reply_text("Sorry, an error occurred! Please try again later.")
        logging.error(
            "Add - DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\""
            .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID)
        )
    return ConversationHandler.END



def remove(update: Update, contex: CallbackContext) -> int:
    "Handle remove command"
    update.message.reply_text(
        "Please mention the user who you want to care about in reply of this message. Send /cancel to cancel."
    )
    return MenuLevels.GET_USER



def removeDC(update: Update, contex: CallbackContext) -> int:
    "Remove a don't care"
    ndc = createDC(update)

    if ndc == None:
        update.effective_message.reply_text("There is no mention in your message, please try again.")
        return None

    for dc in DoesntCare.dcList:
        if dc == ndc:
            if dc.remove():
                update.effective_message.reply_text("Removed user from your don't care list!")
                logging.info(
                    "Remove: DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\""
                    .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID)
                )
            else:
                update.effective_message.reply_text("Sorry, an error occurred! Please try again later.")
                logging.error(
                    "Remove - DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\""
                    .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID)
                )
            return ConversationHandler.END

    update.effective_message.reply_text("You already care about this user!")
    logging.info(
        "Not exists:  DCU: \"{}\" - NIU: \"{}\" - Chat: \"{}\""
        .format(ndc.doesntCareID, ndc.notImportantID, ndc.chatID)
    )
    return ConversationHandler.END



def cancel(update: Update, contex: CallbackContext) -> int:
    "Cancel current operation"
    update.effective_message.reply_text("Operation canceled.", reply_markup=ReplyKeyboardRemove(selective=True))
    return ConversationHandler.END



def message(update: Update, contex: CallbackContext) -> None:
    "Check message for doesn't care cases and response if required"
    username = update.effective_user.username
    userID = update.effective_user.id

    for dc in DoesntCare.dcList:
        if ((dc.notImportantID == username or dc.notImportantID == userID) and
            dc.chatID==update.effective_chat.id):
            try:
                DoesntCareUser = update.effective_chat.get_member(user_id=dc.doesntCareID).user
            except:
                #Probably user left the chat
                dc.remove()
                return

            if not dc.shouldResponse(): return

            update.effective_message.reply_text(DoesntCareUser.full_name + " doesn't care!")