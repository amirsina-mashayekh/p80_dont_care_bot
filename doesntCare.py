import datetime

import data


class DoesntCare:
    """Holds data about who doesn't care who"""

    class ResponseMode:
        INSTANT, TIME, MESSAGE_COUNT = range(3)

    def __init__(self, chat_id: int, not_important_id: str, doesnt_care_id: int, response_mode: int = 0,
                 response_mode_option: float = 0, last_response_dt: datetime.datetime = datetime.datetime.min,
                 response_counter: int = 1) -> None:
        self.chat_id = chat_id
        self.not_important_id = not_important_id
        self.doesnt_care_id = doesnt_care_id
        self.response_mode = response_mode
        self.response_mode_option = response_mode_option
        self.last_response_dt = last_response_dt
        self.response_counter = response_counter

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
            if (datetime.datetime.now() - self.last_response_dt).total_seconds() > self.response_mode_option:
                self.last_response_dt = datetime.datetime.now()
                return True

        elif self.response_mode == DoesntCare.ResponseMode.MESSAGE_COUNT:
            if self.response_counter <= 1:
                self.response_counter = self.response_mode_option
                return True
            else:
                self.response_counter -= 1
                self.update()

        return False

    def add(self) -> bool:
        return data.insert(self)

    def update(self) -> bool:
        return data.update(self)

    def remove(self) -> bool:
        return data.remove(self)
