# from yandex_cloud_ml_sdk import YCloudML
from typing import List

import requests


import re
import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_FOLDER= os.getenv('YANDEX_CLOUD_FOLDER')
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')


# sdk = YCloudML(
#     folder_id=YANDEX_FOLDER,
#     auth=YANDEX_TOKEN,
# )

class GPT():

    def __init__(self):
        pass

    def run(self, messages, tools):

        response = requests.post(
            'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
            headers={
                'Authorization': f'Api-Key {YANDEX_TOKEN}',
                'x-folder-id': f'{YANDEX_FOLDER}'
            },
            json={
                "modelUri": f"gpt://{YANDEX_FOLDER}/yandexgpt",
                "tools": tools,
                "messages": messages,
            }
        )

        return response.json()['result']['alternatives'][0]




messages = [
    {"role": "system", "text": " "},
    {"role": "user", "text": "Какая погода в Москве и в Питере?"},
]

tools = [ {
        "function": {
            "name": "weatherTool",
            "description": "Получает текущую погоду в указанном городе.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Название города, например, Москва"
                    }
                },
                "required": [
                    "city"
                ]
            }
        }
    }
]

# model = sdk.models.completions("yandexgpt", model_version="rc").configure(temperature=0.5)
reminders = []

gpt = GPT()

while True:

    request_body = {
        "messages": messages,
        "tools": tools,
    }

    

    response = gpt.run(messages, tools)

    print (response)

    break

    # # result = model.run(messages)
    # print(result)
    # respond = result.alternatives[0].text
    # print('!assistant:', f'{respond}')

    # m = { "role": "assistant", "text": respond }
    # messages += [m]

    # text = input("!user: ")

    # if text != "":
        
    #     m = { "role": "user", "text": text }

    #     messages += [m]
    