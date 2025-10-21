from typing import List

class StatusManager:
    """
    Quản lý thông báo cho pipeline.
    """
    def __init__(self):
        self.messages: List[str] = []
        self.logs: List[str] = []
        self.state: str = ""

    def add(self, msg: str):
        print(msg)
        self.messages.append(msg)
        self.logs.append(msg)
        self.state = msg

    def reset(self):
        self.messages.clear()
        self.logs.clear()
        self.state = ""

# Singleton
status_manager = StatusManager()