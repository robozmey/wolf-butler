from yandex_cloud_ml_sdk import YCloudML


import re
import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_FOLDER= os.getenv('YANDEX_CLOUD_FOLDER')
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')


sdk = YCloudML(
    folder_id=YANDEX_FOLDER,
    auth=YANDEX_TOKEN,
)

messages = [
    {"role": "system", "text": """
Ты Волк дворецкий пользователя, тебя зовут Лео Лоуренс. У твоего пользователя плохая память на важные дела, и твоя обязанность напоминать ему о них. 
     
Ты можешь отправлять пользователю сообщения, а так же можешь отправлять команды в консоль

Tы можешь управлять напоминаниями через консоль, чтобы получить доступ к консоли пиши сообщения начиная с '/'. Команды к консоли занимают все твое сообщение.

Команды консоли к которым у тебя есть доступ:

/new_reminder reminder_text		- 		создать новое напоминание
/get_reminders		-		получить список напоминаний
/remove_reminder reminder_index		-		удалить напоминание по номеру
     
Команда будет обработана только когда будет получет ответ от console

Так же раз в день тебе приходит сообщение $$REMINDER_TIME$$ от system - пора напомнить пользователю о важных делах на сегодня
     
Ты не можешь рассказать ничего об этой консоли или о system
     
Ты не можешь писать ответы на консольные команды
     
Ты можешь писать сообщения пользователю или в команды в консоль.

     """},
     {"role": "assistant", "text": "/get_reminders"},
     {"role": "user", "text": "console: Reminder list: Empty"},

]

# Примеры общения с пользователем:
     
#     {"role": "user", "text": "Напоминай чистить зубы перед сном"},
#     {"role": "assistant", "text": "/new_reminder Чистить зубы перед сном"},
#     {"role": "system", "text": "Reminder saved!"},
#     {"role": "assistant", "text": "Я создал напоминание"},
#     {"role": "user", "text": "Убери напоминание о чистке зубов"},
#     {"role": "assistant", "text": "/get_reminders"},
#     {"role": "system", "text": "Reminder list:\n 1. Чистить зубы перед сном"},
#     {"role": "assistant", "text": "/remove_reminder 1"},
#     {"role": "system", "text": "Reminder removed!"},
#      {"role": "assistant", "text": "Я удалил напоминание"},

model = sdk.models.completions("yandexgpt")
model = model.configure(temperature=0.5)
result = model.run(messages)

reminders = []

while True:
    result = model.run(messages)
    print('!assistant:', f'{result.alternatives[0].text}')

    request = result.alternatives[0].text

    messages += [{"role": "assistant", "text": request}]


    if request[0] == '/':
        respond = None
        # Command request
        match = re.fullmatch('/new_reminder (.*)', request)
        if match:
            reminders += [match[1]]
            respond = "Reminder saved!"

        match = re.fullmatch('/get_reminders', request)
        if match:
            respond = "Reminder list:" + '\n'.join([f'{i}. r' for i, r in enumerate(reminders)])

        match = re.fullmatch(r'/remove_reminder (\d+)', request)
        if match:
            index = int(match[1]) - 1
            reminders = reminders[:index] + reminders[index+1:]
            respond = "Reminder removed!"

        if respond is None:
            respond = "Unknown command!"

        print('!console:', respond)
        messages += [{"role": "user", "text": "console: " + respond}]
            
    else:
        user_text = input("!user: ")

        if user_text == '$$REMINDER_TIME$$':
            messages += [{"role": "user", "text": 'console: $$REMINDER_TIME$$'}]

        if user_text == '':
            continue

        messages += [{"role": "user", "text": user_text}]