from typing import List

import psycopg2

from session import Session
from tools.reminder_tools_general import Reminder

class Storage():

    class Sessions():

        def __init__(self, storage):
            self.storage = storage
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

        def __init__(self, storage):
            self.storage = storage

        def get(self, chat_id: int) -> List[Reminder]:
            records = self.storage.db_execute(
                "SELECT reminder_id, reminder_time, reminder_text FROM reminders WHERE chat_id = %s ORDER BY reminder_id", 
                [chat_id]
            )

            reminds = []

            for r in records:
                reminder_id = r[0]
                reminder_time = r[1].isoformat(timespec='minutes')
                reminder_text = r[2]

                reminds += [Reminder(reminder_text, reminder_time, reminder_id)]

            return reminds

        def add(self, chat_id: int, reminder: Reminder) -> None:

            self.storage.db_execute(
                "INSERT INTO reminders (chat_id, reminder_time, reminder_text) VALUES (%s, %s, %s)", 
                [chat_id, reminder.time, reminder.text]
            )

        def remove(self, chat_id: int, reminder_id: int) -> None:

            self.storage.db_execute(
                "DELETE FROM reminders WHERE chat_id = %s AND reminder_id = %s", 
                [chat_id, reminder_id]
            )

        def remove_all(self, chat_id: int) -> None:

            self.storage.db_execute(
                "DELETE FROM reminders WHERE chat_id = %s", 
                [chat_id]
            )
        
        def get_by_interval(self, chat_id: int, time_start: str, time_end: str) -> List[Reminder]:
            return list(filter(lambda r: time_start <= r.time and r.time <= time_end, self.get(chat_id)))
    

    def db_commit(self):
        self.connection.commit()

    def db_execute(self, query: str, data_tuple = None):
        cursor = self.connection.cursor()
        cursor.execute(query, data_tuple)
        self.db_commit()
        records = []
        if cursor.pgresult_ptr is not None:
            records = cursor.fetchall()
        self.db_commit()
        cursor.close()
        return records

    def __init__(self):
        self.connection = psycopg2.connect(
            dbname='wolf_butler_database', user='admin', 
            password='WeRy_HaRt_paroll', host='89.169.164.126', port='6000'
        )
        self.reminders = self.Reminders(self)
        self.sessions = self.Sessions(self)

