#!/usr/bin/env python3

from __future__ import annotations

from yandex_cloud_ml_sdk import YCloudML

import os
# from dotenv import load_dotenv

# load_dotenv()

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
    def process(self, obj, context):
        text = obj["text"]

        context.bot.send_message(context.chat_id, text)

        return []
    
class TelegramDebugTool():
    name = "debug"
    def process(self, obj, context):
        context.bot.send_message(context.chat_id, f'<code>{str(obj)}</code>', parse_mode='HTML')

        return []

class RemindersTool():
    name = "reminders"

    def execute(self, command, context):

        reminders = context.session.reminders

        # Command request
        match = re.fullmatch(r'/new_reminder (.*)', command)
        if match:
            reminders.add_reminder(match[1])
            return "Reminder created!"

        match = re.fullmatch(r'/get_reminders', command)
        if match:
            if len(reminders) > 0:
                return "Reminder list: \n" + '\n'.join([f'{i+1}. {r}' for i, r in enumerate(reminders.get_reminders())])
            else:
                return "Reminder list: Empty"

        match = re.fullmatch(r'/remove_reminder (\d+)', command)
        if match:
            index = int(match[1]) - 1
            reminders.remove_reminder(index)
            return "Reminder removed!"

        return "Unknown command!"


    def process(self, obj, context):
        result = self.execute(obj["command"], context)
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
    
    def system_send(self, messages, system_message):
        new_messages = messages + [{"role": "system", "text": system_message}]
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
        result = []
        for tool in self.tools:
            if obj["tool"] == tool.name or tool.name == "debug":
                result += tool.process(obj, context)
            
        return result


    def process_commands(self, objs, context=None):
        messages = []
        for obj in objs:
            messages += self.process_command(obj, context)

        return messages
    
    def invoke_and_process(self, messages, context):
        messages = self.invoke(messages)
        messages += self.process_commands(self.parse_response(messages[-1]), context)

        return messages
    
    def user_send_and_process(self, messages, user_message, context):
        messages = self.user_send(messages, user_message)
        messages += self.process_commands(self.parse_response(messages[-1]), context)

        return messages
    
    def system_send_and_process(self, messages, system_message, context):
        messages = self.system_send(messages, system_message)
        messages += self.process_commands(self.parse_response(messages[-1]), context)

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