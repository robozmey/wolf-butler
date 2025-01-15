# reminder - { "time": "12:00" or None, "text": str}
class Reminder():
    def __init__(self, text: str, time: str = None, reminder_id: int = None):
        self.reminder_id = reminder_id
        self.text = text
        self.time = time

    def __str__(self):
        return f'{{reminder_id={self.reminder_id}, reminder_time={self.time}, reminder_text={self.text}}}'