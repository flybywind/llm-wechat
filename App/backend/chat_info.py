import enum
import json
import time

from pydantic import BaseModel, computed_field

class RoleName(enum.Enum):
    """用户角色"""
    You = "user"
    AI = "ai"

class ChatInfo(BaseModel):
    id: int
    content: str = ""
    name: RoleName = RoleName.AI
    timestamp: int = 0
    @computed_field
    def type(self) -> str:
        return self.name.value

    def js(self):
        d = self.model_dump()
        d["name"] = self.name.name
        return d


if __name__ == "__main__":
    import json

    chat_info = ChatInfo(id=1, content="hello", name=RoleName.You, timestamp=123456)
    print(chat_info.js())
