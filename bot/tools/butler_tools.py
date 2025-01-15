import re

from storage import Storage
from session import Session
from context import ChatContext

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
    