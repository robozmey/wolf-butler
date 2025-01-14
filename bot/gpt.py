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

#       Напоминай о дипломе

#       $$REMINDER_EVENT$$

messages = [
    {"role": "system", "text": },
    #  {"role": "assistant", "text": ""},

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

model = sdk.models.completions("yandexgpt").configure(temperature=0.5)
result = model.run(messages)

reminders = []

while True:
    result = model.run(messages)
    print('!assistant:', f'{result.alternatives[0].text}')

    request = result.alternatives[0].text


    if request[0] == '/':
        request = request.split('\n')[0]

        messages += [{"role": "assistant", "text": request}]

        respond = None
        # Command request
        match = re.fullmatch('/new_reminder (.*)', request)
        if match:
            reminders += [match[1]]
            respond = "Reminder created!"

        match = re.fullmatch('/get_reminders', request)
        if match:
            if len(reminders) > 0:
                respond = "Reminder list: \n" + '\n'.join([f'{i+1}. {r}' for i, r in enumerate(reminders)])
            else:
                respond = "Reminder list: Empty"

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
        messages += [{"role": "assistant", "text": request}]

        user_text = input("!user: ")

        if user_text == '$$REMINDER_TIME$$':
            messages += [{"role": "user", "text": 'console: $$REMINDER_TIME$$'}]


        if user_text == '/retry':
            messages = messages[:-1]
            continue

        if user_text == '':
            continue

        messages += [{"role": "user", "text": user_text}]