# reminder - { "time": "12:00" or None, "text": str}
class Reminder():
    def __init__(self, text: str, time: str = None):
        self.text = text
        self.time = time

    def __str__(self):
        if self.time is None:
            return self.text
        else:
            return f'{self.time} {self.text}'