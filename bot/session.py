#!/usr/bin/python3

from __future__ import annotations

from typing import List, Dict


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

import xml.etree.ElementTree as ET

def export_messages(messages: List[Dict]) -> str:
    data_xml = ET.Element('messages')

    for m in messages:
        message_xml = ET.SubElement(data_xml, 'message')
        message_xml_role = ET.SubElement(message_xml, 'role')
        message_xml_role.text = m["role"]
        message_xml_text = ET.SubElement(message_xml, 'text')
        message_xml_text.text = m["text"]

    return ET.tostring(data_xml, encoding='unicode')

def import_messages(messages_text: str) -> List[Dict]:
    xml_root = ET.fromstring(messages_text)

    messages = []

    for message_xml in xml_root:
        message = {}
        for e in message_xml:
            message[e.tag] = e.text

        messages += [message]

    return messages



class Session():
    def __init__(self, chat_id: int, messages):
        self.chat_id = chat_id
        self.messages = messages