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
        
        match = re.fullmatch(r'/new_reminder_with_time (\d\d:\d\d) (.*)', command)
        if match:
            reminder_text = match[2]
            reminder_time = match[1]
            reminders.add_reminder(reminder_text, reminder_time)
            return "Reminder created!"

        match = re.fullmatch(r'/get_reminders', command)
        if match:
            if len(reminders) > 0:
                return "Reminder list: \n" + '\n'.join([f'{i+1}. {r}' for i, r in enumerate(reminders.get_reminders())])
            else:
                return "Reminder list: Empty"
            
        match = re.fullmatch(r'/get_reminders_by_time (.*)', command)
        if match:
            time = match[1]
            if len(reminders) > 0:
                return "Reminder list: \n" + '\n'.join([f'{i+1}. {r}' for i, r in enumerate(reminders.get_reminders_by_time(time))])
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