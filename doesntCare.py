import datetime


class DoesntCare:
    """Holds data about who doesn't care who"""

    class ResponseMode:
        INSTANT, TIME, MESSAGE_COUNT = range(3)

    dcList = []

    def __init__(self, chat_id: int, not_important_id: int, doesnt_care_id: int, response_mode: int = 0,
                 response_mode_option=0) -> None:
        self.chat_id = chat_id
        self.not_important_id = not_important_id
        self.doesnt_care_id = doesnt_care_id
        self.response_mode = response_mode
        self.response_mode_option = response_mode_option
        self.last_response_dt = datetime.datetime.min
        self.response_counter = 1

        if response_mode == DoesntCare.ResponseMode.TIME:
            if type(response_mode_option) is not datetime.timedelta:
                raise TypeError("type of response_mode_option doesn't match response_mode")

        elif response_mode == DoesntCare.ResponseMode.MESSAGE_COUNT:
            if type(response_mode_option) is not int:
                raise TypeError("type of response_mode_option doesn't match response_mode")

    def __eq__(self, other) -> bool:
        if self.__class__ != other.__class__:
            return False

        if (self.chat_id == other.chat_id and
                self.doesnt_care_id == other.doesnt_care_id and
                self.not_important_id == other.not_important_id):
            return True

    def should_response(self):
        if self.response_mode == DoesntCare.ResponseMode.INSTANT:
            return True

        elif self.response_mode == DoesntCare.ResponseMode.TIME:
            if datetime.datetime.now() - self.last_response_dt > self.response_mode_option:
                self.last_response_dt = datetime.datetime.now()
                return True

        elif self.response_mode == DoesntCare.ResponseMode.MESSAGE_COUNT:
            if self.response_counter <= 1:
                self.response_counter = self.response_mode_option
                return True
            else:
                self.response_counter -= 1

        return False

    def add(self) -> bool:
        DoesntCare.dcList.append(self)
        return True

    def remove(self) -> bool:
        DoesntCare.dcList.remove(self)
        return True
