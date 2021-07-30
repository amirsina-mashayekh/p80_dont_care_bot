from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, messagehandler
from telegram.ext.callbackcontext import CallbackContext
import datetime


class DoesntCare:
    "Holds data about who doesn't care who"

    class ResponseMode:
        INSTANT, TIME, MESSAGE_COUNT = range(3)

    dcList = []

    def __init__(self, chatID: int, notImportantID: int, doesntCareID: int, responseMode: int = 0, responseModeOption = 0) -> None:
        self.chatID = chatID
        self.notImportantID = notImportantID
        self.doesntCareID = doesntCareID
        self.responseMode = responseMode
        self.responseModeOption = responseModeOption

        if responseMode == DoesntCare.ResponseMode.TIME:
            if type(responseModeOption) is not datetime.timedelta: raise "type of responseModeOption doesn't match responseMode"
            self.responseCounter = datetime.datetime.min

        elif responseMode == DoesntCare.ResponseMode.MESSAGE_COUNT:
            if type(responseModeOption) is not int: raise "type of responseModeOption doesn't match responseMode"
            self.responseCounter = 1

    def __eq__(self, other) -> bool:
        if self.__class__ != other.__class__: return False

        if (self.chatID == other.chatID and
            self.doesntCareID == other.doesntCareID and
            self.notImportantID == other.notImportantID):
            return True

    def shouldResponse(self):
        if self.responseMode == DoesntCare.ResponseMode.INSTANT: return True

        elif self.responseMode == DoesntCare.ResponseMode.TIME: 
            if datetime.datetime.now() - self.responseCounter > self.responseModeOption:
                self.responseCounter = datetime.datetime.now()
                return True

        elif self.responseMode == DoesntCare.ResponseMode.MESSAGE_COUNT:
            if self.responseCounter <= 1:
                self.responseCounter = self.responseModeOption
                return True
            else: self.responseCounter -= 1

        return False

    def add(self) -> bool:
        DoesntCare.dcList.append(self)
        return True

    def remove(self) -> bool:
        DoesntCare.dcList.remove(self)
        return True