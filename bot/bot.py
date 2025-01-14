#!/usr/bin/python

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

from butler import TelegramSayTool, RemindersTool, Butler
from promts import butler_promt, butler_message_format, butler_entry_message

butler_desc = butler_promt + butler_message_format

tools = [TelegramSayTool(None, None), RemindersTool()]

butler = Butler(sdk, butler_desc, tools)

messages = []

def setup_butler():
    global butler
    global messages

    butler_desc = butler_promt + butler_message_format

    tools = [TelegramSayTool(None, None), RemindersTool()]

    butler = Butler(sdk, butler_desc, tools)

    messages = [{"role": "system", "text": butler_desc}, {"role": "assistant", "text": butler_entry_message}]

####


@bot.message_handler(commands=['start', 'reset'])
def send_welcome(message):
    global messages

    bot.send_chat_action(message.chat.id, "typing")

    setup_butler()

    context = (bot, message.chat.id)

    messages += butler.process_commands(butler.parse_response(messages[-1]), context)

    # bot.reply_to(message, "Hi! Use /set <seconds> to set a timer")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    global messages

    bot.send_chat_action(message.chat.id, "typing")

    messages = butler.user_send(messages, message.text)

    print(messages)

    context = (bot, message.chat.id)

    messages += butler.process_commands(butler.parse_response(messages[-1]), context)

    if messages[-1]["role"] == "system":
        messages = butler.invoke(messages)

        print(messages)

        messages += butler.process_commands(butler.parse_response(messages[-1]), context)



if __name__ == '__main__':
    # threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    setup_butler()

    bot.infinity_polling()
    