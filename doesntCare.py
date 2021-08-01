import datetime


class DoesntCare:
    """Holds data about who doesn't care who"""

    class ResponseMode:
        INSTANT, TIME, MESSAGE_COUNT = range(3)

    dcList = []

    def __init__(self, chat_id: int, not_important_id: int, doesnt_care_id: int, response_mode: int = 0,
                 response_mode_option=0) -> None:
        self.chatID = chat_id
        self.notImportantID = not_important_id
        self.doesntCareID = doesnt_care_id
        self.responseMode = response_mode
        self.responseModeOption = response_mode_option
        self.lastResponseDT = datetime.datetime.min
        self.responseCounter = 1

        if response_mode == DoesntCare.ResponseMode.TIME:
            if type(response_mode_option) is not datetime.timedelta:
                raise TypeError("type of responseModeOption doesn't match responseMode")

        elif response_mode == DoesntCare.ResponseMode.MESSAGE_COUNT:
            if type(response_mode_option) is not int:
                raise TypeError("type of responseModeOption doesn't match responseMode")

    def __eq__(self, other) -> bool:
        if self.__class__ != other.__class__:
            return False

        if (self.chatID == other.chatID and
                self.doesntCareID == other.doesntCareID and
                self.notImportantID == other.notImportantID):
            return True

    def should_response(self):
        if self.responseMode == DoesntCare.ResponseMode.INSTANT:
            return True

        elif self.responseMode == DoesntCare.ResponseMode.TIME:
            if datetime.datetime.now() - self.lastResponseDT > self.responseModeOption:
                self.lastResponseDT = datetime.datetime.now()
                return True

        elif self.responseMode == DoesntCare.ResponseMode.MESSAGE_COUNT:
            if self.responseCounter <= 1:
                self.responseCounter = self.responseModeOption
                return True
            else:
                self.responseCounter -= 1

        return False

    def add(self) -> bool:
        DoesntCare.dcList.append(self)
        return True

    def remove(self) -> bool:
        DoesntCare.dcList.remove(self)
        return True
