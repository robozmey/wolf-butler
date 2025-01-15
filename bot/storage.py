from typing import List

from session import Session

from tools.reminder_tools_general import Reminder

class Storage():

    class Sessions():

        def __init__(self):
            self.sessions = {}

        def list(self) -> List[int]:
            return list(self.sessions.keys())

        def get(self, chat_id: int) -> Session:
            if chat_id not in self.sessions:
                self.sessions[chat_id] = Session(chat_id)

            return self.sessions[chat_id]

        def set(self, chat_id: int, session: Session) -> None:
            self.sessions[chat_id] = session

        def reset(self, chat_id: int) -> Session:
            self.sessions[chat_id] = Session(chat_id)
            return self.sessions[chat_id]

    class Reminders():

        def __init__(self):
            self.remainder_list = {}

        def get_or_create(self, chat_id: int):
            if chat_id not in self.remainder_list:
                self.remainder_list[chat_id] = []
           
            return self.remainder_list[chat_id]

        def get(self, chat_id: int) -> List[Reminder]:
            return self.get_or_create(chat_id)

        def add(self, chat_id: int, reminder: Reminder) -> None:
            self.remainder_list[chat_id] = self.get_or_create(chat_id) + [reminder]

        def remove(self, chat_id: int, reminder_id_in_list: int) -> None:
            remainder_list = self.get_or_create(chat_id)

            self.remainder_list[chat_id] = remainder_list[:reminder_id_in_list] + remainder_list[reminder_id_in_list+1:]
        
        def get_by_interval(self, chat_id: int, time_start: str, time_end: str) -> List[Reminder]:
            return list(filter(lambda r: time_start <= r.time and r.time <= time_end, self.get(chat_id)))

    def __init__(self):
        self.connection = ""
        self.reminders = self.Reminders()
        self.sessions = self.Sessions()

