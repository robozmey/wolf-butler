#!/usr/bin/python3

from __future__ import annotations

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

import asyncio
import logging
import sys
import os
import time, threading, schedule
from dotenv import load_dotenv
load_dotenv()

import telebot
from telebot import types


# Bot token can be obtained via https://t.me/BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')
YANDEX_FOLDER = os.getenv('YANDEX_CLOUD_FOLDER')
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

bot = telebot.TeleBot(BOT_TOKEN)

#####

from yandex_cloud_ml_sdk import YCloudML

sdk = YCloudML(
    folder_id=YANDEX_FOLDER,
    auth=YANDEX_TOKEN,
)

#####

from tools.butler_tools import TelegramSayTool, TelegramDebugTool
from tools.reminder_tools import RemindersTool
from tools.time_tool import TimeTool
from butler import Butler

from promts import butler_promt, butler_message_format, butler_desc

tools = [TelegramSayTool(), RemindersTool(), TimeTool()]

butler = Butler(sdk, butler_desc, tools)

def setup_butler():
    global butler
    butler = Butler(sdk, butler_desc, tools)

setup_butler()

from storage import Storage, StorageSettings

storage_settings = StorageSettings(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD)
storage = Storage(butler, storage_settings)

from session import Session
from context import SessionMaster, ChatContext

sessionMaster = SessionMaster(storage)

import datetime




class Scheduler():
    def __init__(self):
        self.previous_remind_time = (datetime.datetime.now() - datetime.timedelta(minutes=1)).time().isoformat(timespec='minutes')

    def remind(self):
        prev_time = self.previous_remind_time
        now_time = datetime.datetime.now().time().isoformat(timespec='minutes')
        logging.info(f"Remind time: {now_time}")
        
        for session_id in sessionMaster.list():
            session = sessionMaster.get_session(session_id)

            current_reminders = storage.reminders.get_by_interval(session_id, prev_time, now_time)

            if len(current_reminders) > 0:

                context = ChatContext(session, bot, storage)

                text = f"Текущее время: {now_time}\nНапомни пользователю о:\n"

                for r in current_reminders:
                    text += str(r)

                session.messages = butler.system_send_and_process(session.messages, text, context)
                if session.messages[-1]["role"] == "system":
                    session.messages = butler.invoke_and_process(session.messages, context)
                # session.messages = butler.invoke_and_process(session.messages, context)

                sessionMaster.set_session(session_id, session)

        self.previous_remind_time = now_time


scheduler = Scheduler()

schedule.every(2).minutes.do(scheduler.remind)
# schedule.every().day.at("20:35").do(remind)
    
####

@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):

    chat_id = message.chat.id
    session = sessionMaster.reset_session(chat_id)

    bot.send_chat_action(chat_id, "typing")

    context = ChatContext(session, bot, storage)

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

    if len(out) > 1000:
        out = out[-1000:]

    bot.send_message(chat_id, out)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def text_message(message):

    chat_id = message.chat.id
    session = sessionMaster.get_session(chat_id)

    bot.send_chat_action(message.chat.id, "typing")

    context = ChatContext(session, bot, storage)
    session.messages = butler.user_send_and_process(session.messages, message.text, context)

    if session.messages[-1]["role"] == "system":
        session.messages = butler.invoke_and_process(session.messages, context)

    sessionMaster.set_session(chat_id, session)



if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    setup_butler()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Bot Started")

    while True:
        schedule.run_pending()
        time.sleep(1)
    