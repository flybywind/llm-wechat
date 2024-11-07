
import enum
import json

from pydantic import BaseModel


class RoleName(enum.Enum):
  """用户角色"""
  You = "user"
  AI   = "ai"

class ChatInfoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
      if isinstance(obj, enum.Enum):
        return obj.name  # 返回枚举值的名称
      elif isinstance(obj, ChatInfo):
        d = obj.model_dump(mode="python")
        d["type"] = obj.name.value
        return d
      return super().default(obj) 

class ChatInfo(BaseModel):
  id: int
  content: str = ""
  name: RoleName = RoleName.AI
  timestamp: int = -1
