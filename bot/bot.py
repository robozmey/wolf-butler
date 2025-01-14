#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import asyncio
import logging
import sys
import os
import time, threading, schedule
# from dotenv import load_dotenv
# load_dotenv()

import telebot
from telebot import types


# Bot token can be obtained via https://t.me/BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')
YANDEX_FOLDER= os.getenv('YANDEX_CLOUD_FOLDER')
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

#####

from yandex_cloud_ml_sdk import YCloudML

sdk = YCloudML(
    folder_id=YANDEX_FOLDER,
    auth=YANDEX_TOKEN,
)

#####

from butler import TelegramSayTool, RemindersTool, TelegramDebugTool
from butler import Butler

from promts import butler_promt, butler_message_format, butler_entry_message

butler_desc = butler_promt + butler_message_format

tools = [TelegramSayTool(), RemindersTool()]

butler = Butler(sdk, butler_desc, tools)

DEFAULT_MESSAGES = [{"role": "system", "text": butler_desc}, {"role": "system", "text": "Поприветствуй пользователя"}]

def setup_butler():
    global butler
    global messages

    butler_desc = butler_promt + butler_message_format

    tools = [TelegramSayTool(), RemindersTool(), TelegramDebugTool()]

    butler = Butler(sdk, butler_desc, tools)

####

class ReminderManager():
    def __init__(self):
        self.reminders = []

    def __len__(self):
        return len(self.reminders)
    
    def __str__(self):
        return str(self.reminders)

    def add_reminder(self, text):
        self.reminders += [text]

    def remove_reminder(self, index):
        self.reminders = self.reminders[:index] + self.reminders[index+1:]

    def get_reminders(self):
        return self.reminders

####

class Session():
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.messages = DEFAULT_MESSAGES
        self.reminders = ReminderManager()

class SessionMaster():
    def __init__(self):
        self.sessions = {}

    def get_session(self, id):
        return self.sessions.get(id, Session(id))
    
    def set_session(self, id, session):
        self.sessions[id] = session

sessionMaster = SessionMaster()

class ChatContext():
    def __init__(self, session, bot):
        self.session = session
        self.chat_id = session.chat_id
        self.bot = bot

####

import datetime

def remind():
    print("Remindtion time!")
    for session_id in sessionMaster.sessions:
        session = sessionMaster.get_session(session_id)

        print(session_id, session.reminders)

        if len(session.reminders) > 0:

            context = ChatContext(session, bot)

            now_time = datetime.datetime.now().isoformat()

            session.messages = butler.system_send_and_process(session.messages, f"$$REMINDER_EVENT$$, текущее время: {now_time}", context)
            if session.messages[-1]["role"] == "system":
                session.messages = butler.invoke_and_process(session.messages, context)
            # session.messages = butler.invoke_and_process(session.messages, context)

            sessionMaster.set_session(session_id, session)


# schedule.every(10).seconds.do(remind)
schedule.every().day.at("20:35").do(remind)
    
####

@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):

    chat_id = message.chat.id
    session = Session(chat_id)

    bot.send_chat_action(chat_id, "typing")

    setup_butler()

    context = ChatContext(session, bot)

    session.messages = butler.invoke_and_process(session.messages, context)

    sessionMaster.set_session(chat_id, session)


@bot.message_handler(commands=['history'])
def send_history(message):

    chat_id = message.chat.id
    session = sessionMaster.get_session(chat_id)

    out = ""

    for msg in session.messages:
        out += msg["role"] + ':\n'
        out += msg["text"] + '\n'

    bot.send_message(chat_id, out)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):

    chat_id = message.chat.id
    session = sessionMaster.get_session(chat_id)

    bot.send_chat_action(message.chat.id, "typing")

    context = ChatContext(session, bot)
    session.messages = butler.user_send_and_process(session.messages, message.text, context)

    if session.messages[-1]["role"] == "system":
        session.messages = butler.invoke_and_process(session.messages, context)

    sessionMaster.set_session(chat_id, session)



if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    setup_butler()

    while True:
        schedule.run_pending()
        time.sleep(1)
    