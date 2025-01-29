from butler_tools import BaseTool
from context import ChatContext

memory_tool_api = """
Memory API позволяет тебе использовать Memory хранилище для сохранения информации

{GET|HEAD|PUT|DELETE} /<имя_бакета>/<ключ_объекта>
Request_body

{
    "method": "GET|HEAD|PUT|DELETE", 
    "address": "/<имя_бакета>/<ключ_объекта>"
    "headers": {
        "description": ""
        "priority": true
        "contentType": 
    }
    "body: ""
}

Headers:
- description - описание того что храниться в данной ячейке
- contentType - тип данных сейчас все - text
- priority - Данные отображаются в начале диалога, перед каждым сообщением или вообще не отображаются

У информции в хранилище есть флаги:
- информация сообщается в заголовку диалога
- информация сообщается в перед любым ответом к нейросети
"""

memory_tool_usage = """
Как пользоваться Memory API

В бакете user храниться информация о пользователе и ты её туда сохраняешь

В user/name храниться полное имя пользователя

В user/callname храниться как ты должел обращаться к пользователю

В user/utc храниться часовой пояс пользователя

В user/

"""

class MemoryTool(BaseTool):
    name = "time"

    api_desc = time_tool_api

    def process(self, obj, context: ChatContext):

        if obj['method'] == 'GET':
            context.storage.

        now_time = datetime.datetime.now().time().isoformat(timespec='minutes')
        result = f'Current time: {now_time}'
        message = {"role": "system", "text": result}
        return [message]