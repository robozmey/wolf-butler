from typing import List

import psycopg2
import logging

from session import Session, export_messages, import_messages
from tools.reminder_tools_general import Reminder
from butler import Butler

class StorageSettings():
    dbname='wolf_butler_database'
    user='admin', 
    password='WeRy_HaRt_paroll'

    host='89.169.164.126'
    port='6000'

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

class Storage():

    class Sessions():

        def __init__(self, storage, butler: Butler):
            self.storage = storage
            self.butler = butler

        def list(self) -> List[int]:
            records = self.storage.db_execute(
                "SELECT chat_id FROM sessions", 
            )
            return [r[0] for r in records]

        def get(self, chat_id: int) -> Session:

            records = self.storage.db_execute(
                "SELECT message_list FROM sessions WHERE chat_id = %s", 
                [chat_id]
            )
            
            sessions = Session(chat_id, import_messages(records[0][0]))

            return sessions

        def set(self, chat_id: int, session: Session) -> Session:

            message_list = export_messages(session.messages)

            # logging.debug(f'message_list: {message_list}')

            self.storage.db_execute(
                "UPDATE sessions SET message_list = XMLPARSE(DOCUMENT %s) WHERE chat_id = %s", 
                [message_list, chat_id]
            )

            return session

        def new(self, chat_id: int) -> bool:

            self.storage.db_execute(
                "INSERT INTO sessions (chat_id) VALUES(%s)", 
                [chat_id]
            )
            
            return True

        def reset(self, chat_id: int) -> Session:

            self.new(chat_id)

            return self.set(chat_id, self.butler.new_session(chat_id))

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
            all_reminders = self.get(chat_id)
            if time_start <= time_end:
                return list(filter(
                    lambda r: (time_start < r.time or time_start < r.time and time_start == time_end) and r.time <= time_end, 
                    all_reminders
                ))
            else:
                return list(filter(
                    lambda r: time_end <= r.time or r.time <= time_start, 
                    all_reminders
                ))
            
    

    def db_commit(self):
        self.connection.commit()

    def db_execute(self, query: str, data_tuple = None):

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data_tuple)
            self.db_commit()
            records = []
            if cursor.pgresult_ptr is not None:
                records = cursor.fetchall()
            self.db_commit()
            cursor.close()
        except Exception as e:
            logging.warning(f'Caught exception executing sql: {e}')
            self.db_commit()
            return None
                
        return records

    def __init__(self, butler: Butler, settings: StorageSettings):
        self.connection = psycopg2.connect(
            dbname=settings.dbname, 
            user=settings.user, 
            password=settings.password, 
            host=settings.host, 
            port=settings.port
        )
        self.butler = butler
        self.reminders = self.Reminders(self)
        self.sessions = self.Sessions(self, butler)

