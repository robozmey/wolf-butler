import re

from storage import Storage
from session import Session
from context import ChatContext

from tools.butler_tools import BaseTool

from tools.reminder_tools_general import Reminder

reminder_tool_api = """
# Reminders API 

API позволяет тебе управлять ежедневными напоминаниями. Когда прийдет время которое ты указал у напоминания {{system}} сообщит тебе о том, какие напоминания есть на текущий момент и о чем нужно напомнить пользователю

Tы управляешь напоминаниями через консоль ("tool":"reminders"), чтобы получить доступ к консоли пиши сообщения начиная с '/' по одной команде на новой строке. Команды к консоли занимают все твое сообщение.
     
После вызова команды нужно подождать. Команда будет обработана только когда будет получет ответ от console: "Reminder created!" или "Reminder removed!"
     
Напомнинание не счистается созданым если не была вызвана команда

Напоминания удаляются только по запросу пользователя
     
Каждый раз когда пользователь просит посмотреть, добавить или удалить напоминания ты должен сразу, без промедлений отправить команду в консоль.

Команды консоли к которым у тебя есть доступ:
{"tool": "reminders", "command": "/new_reminder reminder_text"}     	- 		создать новое напоминание
{"tool": "reminders", "command": "/new_reminder_with_time время_напоминания(HH:MM) текст_напоминания"}		- 		создать новое напоминание со временем когда напоминать
{"tool": "reminders", "command": "/get_reminders"}		-		получить список напоминаний
{"tool": "reminders", "command": "/get_reminders_by_time время_напоминания"}		-		получить список напоминаний на определеное время
{"tool": "reminders", "command": "/remove_reminder reminder_index"}		-		удалить напоминание по номеру
{"tool": "reminders", "command": "/remove_all_reminders"} 		-		удалить удалить все напоминания

Команды /get возвращают результат в таком формате
    Reminder list: 
    {reminder_id=ID_НАПОМИНАНИЯ}, reminder_time=ВРЕМЯ_НАПОМИНАНИЯ, reminder_text=ТЕКСТ_НАПОМИНАНИЯ}
    {reminder_id=ID_НАПОМИНАНИЯ}, reminder_time=ВРЕМЯ_НАПОМИНАНИЯ, reminder_text=ТЕКСТ_НАПОМИНАНИЯ}
    {reminder_id=ID_НАПОМИНАНИЯ}, reminder_time=ВРЕМЯ_НАПОМИНАНИЯ, reminder_text=ТЕКСТ_НАПОМИНАНИЯ}

Примеры:
Пользователь: Напомни мне в 12:30 про встеру с Сережей
Ты: {"tool": "reminders", "command": "/new_reminder_with_time 12:30 встреча с Сережей"}

Пользователь: О чем я просил тебя напоминать?
Ты: {"tool": "reminders", "command": "/get_reminders"} 

"""

class RemindersTool(BaseTool):
    name = "reminders"

    api_desc = reminder_tool_api

    def execute(self, command, context: ChatContext):

        storage = context.storage
        chat_id = context.session.chat_id

        # Command request
        match = re.fullmatch(r'/new_reminder (.*)', command)
        if match:
            storage.reminders.add(chat_id, Reminder(match[1]))
            return "Reminder created!"
        
        match = re.fullmatch(r'/new_reminder_with_time (\d\d:\d\d) (.*)', command)
        if match:
            reminder_text = match[2]
            reminder_time = match[1]
            storage.reminders.add(chat_id, Reminder(reminder_text, reminder_time))
            return "Reminder created!"

        match = re.fullmatch(r'/get_reminders', command)
        if match:
            r_list = storage.reminders.get(chat_id)
            if len(r_list) > 0:
                return "Reminder list: \n" + '\n'.join([str(r) for r in r_list])
            else:
                return "Reminder list: Empty"
            
        match = re.fullmatch(r'/get_reminders_by_time (.*)', command)
        if match:
            time = match[1]
            r_list = storage.reminders.get_by_interval(chat_id, time, time)
            if len(r_list) > 0:
                return "Reminder list: \n" + '\n'.join([f'{i+1}. {r}' for i, r in enumerate(r_list)])
            else:
                return "Reminder list: Empty"

        match = re.fullmatch(r'/remove_reminder (\d+)', command)
        if match:
            index = int(match[1])
            storage.reminders.remove(chat_id, index)
            return "Reminder removed!"
        
        match = re.fullmatch(r'/remove_all_reminders', command)
        if match:
            storage.reminders.remove_all(chat_id)
            return "All reminders removed!"

        return "Error: Unknown command!"


    def process(self, obj, context: ChatContext):
        result = self.execute(obj["command"], context)
        message = {"role": "system", "text": result}
        return [message]