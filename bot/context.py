from typing import List

from storage import Storage
from session import Session

class SessionMaster():
    def __init__(self, storage: Storage):
        self.storage = storage

    def list(self) -> List[int]:
        return self.storage.sessions.list()

    def get_session(self, id: int) -> Session:
        return self.storage.sessions.get(id)
    
    def reset_session(self, id: int) -> Session:
        return self.storage.sessions.reset(id)
    
    def set_session(self, id, session) -> None:
        self.storage.sessions.set(id, session)

class ChatContext():
    def __init__(self, session: Session, bot, storage: Storage):
        self.session = session
        self.chat_id = session.chat_id
        self.bot = bot
        self.storage = storage