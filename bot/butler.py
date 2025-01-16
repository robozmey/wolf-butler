#!/usr/bin/env python3

from __future__ import annotations

from typing import List

from yandex_cloud_ml_sdk import YCloudML

import os
# from dotenv import load_dotenv

# load_dotenv()

YANDEX_FOLDER= os.getenv('YANDEX_CLOUD_FOLDER')
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')

import re
import json

from promts import butler_promt, butler_message_format
from tools.butler_tools import BaseTool
from session import Session

from enum import Enum
class NextAction(Enum):
    ConsoleCommand="запустить консольную команду"
    TextResponse="ответить словами"
    Stop="никак не реагировать"


class Butler():

    def __init__(self, sdk, butler_desc, tools: List[BaseTool]):
        # self.sdk = sdk
        self.butler_desc = butler_desc

        self.tools = tools

        apis_desc = ""

        for tool in tools:
            apis_desc += tool.api_desc + "\n"

        if apis_desc != "":
            self.butler_desc += "# Описания доступных тебе инструментов (API):\n" + apis_desc

        self.choose_model = sdk.models.text_classifiers("yandexgpt").configure(
            task_description= f'Ты раотаешь по следующим правилам {butler_desc}\n' + "Как отреагировать на это сообщение?",
            labels=[
                "запустить консольную команду",
                "ответить словами",
                "никак не реагировать"
            ]
        )

        self.text_model = sdk.models.completions("yandexgpt").configure(temperature=0.5)


    def new_session(self, chat_id: int) -> Session:
        messages = [{"role": "system", "text": self.butler_desc}, {"role": "system", "text": "Поприветствуй пользователя"}]
        return Session(chat_id, messages)


    def how_to_react(self, messages):
        return self.choose_model.run(messages[-1]["text"]) 
    
    def user_send(self, messages, user_message):
        new_messages = messages + [{"role": "user", "text": user_message}]
        return self.invoke(new_messages)
    
    def system_send(self, messages, system_message):
        new_messages = messages + [{"role": "system", "text": system_message}]
        return self.invoke(new_messages)

    def invoke(self, messages):
        # probs = self.how_to_react(messages)

        # reaction_variant = probs.index(max(probs))

        # next_action = max(probs, key=lambda c: c.confidence).label

        return self.text_invoke(messages)

    
    def text_invoke(self, messages):
        respond = self.text_model.run(messages).alternatives[0].text

        m = re.match(r'\{[\s\S]+?\}', respond)
        if m:
            respond = m[0]
            messages += [{"role": "assistant", "text": respond}]

        return messages
    

    def parse_response(self, response):
        objs = []
        for m in re.findall(r'\{[\s\S]+\}', response["text"]):
            # print("1", m)
            try:
                objs += [json.loads(m)]
            except Exception:
                m2 = re.match(r'\{\s*"tool"\s*:\s*"say"\s*,\s*"text"\s*:\s*"([\s\S]*?)"\s*\}', m)
                if m2:
                    objs += [{"tool": "say", "text": m2[1]}]

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
