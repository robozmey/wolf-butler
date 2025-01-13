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
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)


reminders = []


class ReminderMaster():
    def __init__(self):
        self.reminders = []

    def save_reminder(self, reminder):
        self.reminders += [reminder]

    def get_reminders(self):
        return self.reminders


reminder_master = ReminderMaster()


@bot.message_handler(commands=['new_reminder'])
def new_reminder(message):

    args = message.text.split()
    if len(args) > 1:
        reminder = args[1]

        reminder_master.save_reminder(reminder)

        bot.reply_to(message, 'Reminder saved!')
    else:
        bot.reply_to(message, 'Usage: /new_reminder <reminder text>')


@bot.message_handler(commands=['get_reminders'])
def send_welcome(message):
    bot.send_message(message.chat.id, str(reminder_master.get_reminders()))


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Use /set <seconds> to set a timer")


def beep(chat_id) -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text='Beep!')


@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
    else:
        bot.reply_to(message, 'Usage: /set <seconds>')


@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(message.chat.id)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)




if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
    