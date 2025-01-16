class BaseTool():

    api_desc = ""

    def process(obj):
        pass

class SayTool(BaseTool):
    name = "say"
    def process(self, obj):
        print(obj["text"])
        return []
    
class TelegramSayTool(BaseTool):
    name = "say"
    def process(self, obj, context):
        text = obj["text"]

        context.bot.send_message(context.chat_id, text)

        return []
    
class TelegramDebugTool(BaseTool):
    name = "debug"
    def process(self, obj, context):
        context.bot.send_message(context.chat_id, f'<code>{str(obj)}</code>', parse_mode='HTML')

        return []
    