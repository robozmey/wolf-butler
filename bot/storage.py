class Session():
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.messages = DEFAULT_MESSAGES
        self.reminders = ReminderManager()

class Storage():

    class Sessions():

        def __init__(self):
            self.sessions = {}

        def get(self, chat_id):
            return self.sessions.get(chat_id, Session(chat_id))

        def set(self, chat_id, session):
            self.sessions[chat_id] = session

        def reset(self, chat_id):
            self.sessions[chat_id] = Session(chat_id)

    class Reminders():

        def __init__(self):
            self.list = {}

        def get_or_create(self, char_id):
            if chat_id not in self.list:
                self.list[char_id] = []
           
            return self.list[char_id]

        def get(self, chat_id)
            return self.get_or_create(char_id)

        def add(self, chat_id, reminder)
            self.list = self.get_or_create(char_id) + [reminder]

        def remove(self, chat_id, reminder_id_in_list)
            r_list = self.get_or_create(char_id)

            self.list = r_list[:reminder_id_in_list] + r_list[reminder_id_in_list+1:]
        
        def get_by_interval(self, chat_id, time_start, time_end):
            return list(filter(lambda r: time_start <= r.time and r.time <= time_end, self.list))

    def __init__(self):
        self.connection = ""
        self.reminders = self.Reminders()
        self.sessions = self.Sessions()

