import datetime

from tools.butler_tools import BaseTool

time_tool_api = """
# Time API

Ты можешь узнать текущее время через консоль ("tool":"time")

Примеры:

Запрос - {"tool": "time", "command": "/get_time"}
Ответ - Current time: 15:10
"""

class TimeTool(BaseTool):
    name = "time"

    api_desc = time_tool_api

    def process(self, obj, context):
        now_time = datetime.datetime.now().time().isoformat(timespec='minutes')
        result = f'Current time: {now_time}'
        message = {"role": "system", "text": result}
        return [message]