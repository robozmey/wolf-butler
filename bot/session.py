#!/usr/bin/python3

from __future__ import annotations


# class ReminderManager():

#     def __init__(self):
#         self.reminders = []

#     def __len__(self):
#         return len(self.reminders)
    
#     def __str__(self):
#         return str(self.reminders)

#     def add_reminder(self, text: str, time=None):
#         self.reminders += [Reminder(text, time)]

#     def remove_reminder(self, index: int):
#         self.reminders = self.reminders[:index] + self.reminders[index+1:]

#     def get_reminders(self):
#         return self.reminders
    
#     def get_reminders_by_time(self, time: str):
#         return list(filter(lambda r: r.time == time, self.reminders))

####

from promts import DEFAULT_MESSAGES

class Session():
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.messages = DEFAULT_MESSAGES