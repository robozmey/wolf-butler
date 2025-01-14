#!/usr/bin/env python3

from __future__ import annotations

from yandex_cloud_ml_sdk import YCloudML

import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_FOLDER= os.getenv('YANDEX_CLOUD_FOLDER')
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')

import re
import json

from promts import butler_promt, butler_message_format

from enum import Enum
class NextAction(Enum):
    ConsoleCommand="запустить консольную команду"
    TextResponse="ответить словами"
    Stop="никак не реагировать"

class BaseTool():
    def process(obj):
        pass

class SayTool():
    name = "say"
    def process(self, obj):
        print(obj["text"])
        return []
    
class TelegramSayTool():
    name = "say"
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.chat_id = chat_id

    def process(self, obj, context):
        text = obj["text"]

        context[0].send_message(context[1], text)

        return []

class RemindersTool():
    name = "reminders"

    def __init__(self):
        self.reminders_list = []

    def execute(self, command):

        reminders = self.reminders_list

        # Command request
        match = re.fullmatch(r'/new_reminder (.*)', command)
        if match:
            self.reminders_list += [match[1]]
            return "Reminder created!"

        match = re.fullmatch(r'/get_reminders', command)
        if match:
            if len(reminders) > 0:
                return "Reminder list: \n" + '\n'.join([f'{i+1}. {r}' for i, r in enumerate(reminders)])
            else:
                return "Reminder list: Empty"

        match = re.fullmatch(r'/remove_reminder (\d+)', command)
        if match:
            index = int(match[1]) - 1
            self.reminders_list = reminders[:index] + reminders[index+1:]
            return "Reminder removed!"

        return "Unknown command!"


    def process(self, obj, context):
        result = self.execute(obj["command"])
        message = {"role": "system", "text": result}
        return [message]


class Butler():

    def __init__(self, sdk, butler_desc, tools):
        # self.sdk = sdk
        self.butler_desc = butler_desc
        self.choose_model = sdk.models.text_classifiers("yandexgpt").configure(
            task_description= f'Ты раотаешь по следующим правилам {butler_desc}\n' + "Как отреагировать на это сообщение?",
            labels=[
                "запустить консольную команду",
                "ответить словами",
                "никак не реагировать"
            ]
        )

        self.text_model = sdk.models.completions("yandexgpt").configure(temperature=0.5)

        self.tools = tools


    def how_to_react(self, messages):
        return self.choose_model.run(messages[-1]["text"]) 
    
    def user_send(self, messages, user_message):
        new_messages = messages + [{"role": "user", "text": user_message}]
        return self.invoke(new_messages)

    def invoke(self, messages):
        probs = self.how_to_react(messages)

        # reaction_variant = probs.index(max(probs))

        # next_action = max(probs, key=lambda c: c.confidence).label

        return self.text_invoke(messages)

        # if next_action == NextAction.TextResponse.value:

        #     messages += [{"role": "system", "text": "В следующем сообщении отвечай текстом"}]
        #     return self.text_invoke(messages)
        
        # elif next_action == NextAction.ConsoleCommand.value:

        #     messages += [{"role": "system", "text": "В следующем сообщении напиши консольную комманду которую ты запустишь"}]
        #     return self.text_invoke(messages)
        # else:
        #     return messages

    
    def text_invoke(self, messages):
        respond = self.text_model.run(messages).alternatives[0].text
        messages += [{"role": "assistant", "text": respond}]

        return messages
    

    def parse_response(self, response):
        objs = []
        for match in re.findall(r'\{.*?\}', response["text"]):
            objs += [json.loads(match)]

        return objs


    def process_command(self, obj, context):
        for tool in self.tools:
            if obj["tool"] == tool.name:
                return tool.process(obj, context)
            
        return []


    def process_commands(self, objs, context=None):
        messages = []
        for obj in objs:
            messages += self.process_command(obj, context)

        return messages





def main() -> None:
    sdk = YCloudML(
        folder_id=YANDEX_FOLDER,
        auth=YANDEX_TOKEN,
    )
    
    butler_desc = butler_promt + butler_message_format

    tools = [SayTool(), RemindersTool()]

    butler = Butler(sdk, butler_desc, tools)

    messages = [{"role": "system", "text": butler_desc}]

    messages = butler.invoke(messages)

    messages = butler.user_send(messages, "Напомни про диплом")

    messages += butler.process_commands(butler.parse_response(messages[-1]))

    messages = butler.user_send(messages, "Какие есть напоминания?")

    messages += butler.process_commands(butler.parse_response(messages[-1]))

    messages = butler.invoke(messages)

    # print(messages[-1])

    for message in messages[1:]:
        print(f'{message["role"]}:')
        print(message["text"])

if __name__ == '__main__':
    main()