import re

from storage import Storage
from session import Session
from context import ChatContext

from tools.reminder_tools_general import Reminder

class RemindersTool():
    name = "reminders"

    def execute(self, command, context: ChatContext):

        storage = context.storage
        chat_id = context.session.chat_id

        # Command request
        match = re.fullmatch(r'/new_reminder (.*)', command)
        if match:
            storage.reminders.add(chat_id, Reminder(match[1]))
            return "Reminder created!"
        
        match = re.fullmatch(r'/new_reminder_with_time (\d\d:\d\d) (.*)', command)
        if match:
            reminder_text = match[2]
            reminder_time = match[1]
            storage.reminders.add(chat_id, Reminder(reminder_text, reminder_time))
            return "Reminder created!"

        match = re.fullmatch(r'/get_reminders', command)
        if match:
            r_list = storage.reminders.get(chat_id)
            if len(r_list) > 0:
                return "Reminder list: \n" + '\n'.join([str(r) for r in r_list])
            else:
                return "Reminder list: Empty"
            
        match = re.fullmatch(r'/get_reminders_by_time (.*)', command)
        if match:
            time = match[1]
            r_list = storage.reminders.get_by_interval(chat_id, time, time)
            if len(r_list) > 0:
                return "Reminder list: \n" + '\n'.join([f'{i+1}. {r}' for i, r in enumerate(r_list)])
            else:
                return "Reminder list: Empty"

        match = re.fullmatch(r'/remove_reminder (\d+)', command)
        if match:
            index = int(match[1])
            storage.reminders.remove(chat_id, index)
            return "Reminder removed!"
        
        match = re.fullmatch(r'/remove_all_reminders', command)
        if match:
            storage.reminders.remove_all(chat_id)
            return "All reminders removed!"

        return "Unknown command!"


    def process(self, obj, context: ChatContext):
        result = self.execute(obj["command"], context)
        message = {"role": "system", "text": result}
        return [message]