import sys
import threading
import time
import queue
from typing import Generator
import webview
# import uvicorn
# import fastapi
from loguru import logger

from .chat_info import ChatInfo, RoleName


class ChatBackendAPI:
  def __init__(self):
    self.chat_list:ChatInfo = []
    self.quest_queue = queue.Queue(1)
    self.answer_queue = queue.Queue(1)
    self.is_running = True
    self.chain = None
    threading.Thread(target=self.__askquest_worker, daemon=True).start()

  def add_or_update_question(self, idx: int, qest: str):
    if idx == -1:
      idx = len(self.chat_list)
    if idx == len(self.chat_list):
      self.chat_list.append(ChatInfo(id=idx, type=RoleName.You, content=qest, timestamp=int(time.time()*1000)))
      self.chat_list.append(ChatInfo(id=idx+1))
    self.chat_list[idx].content = qest
    self.chat_list[idx+1].content = ""
    self.quest_queue.put(idx)
    return self.chat_list[idx]
  
  def get_answer(self):
    ans:ChatInfo = self.answer_queue.get()
    assert ans is not None and ans.id < len(self.chat_list)
    ans0:ChatInfo = self.chat_list[ans.id]
    if ans0.content == "":
      ans0.timestamp = int(time.time()*1000)
    if ans.content == "<END>":
      return ans0
    
    ans_str = ans0.content + ans.content
    self.chat_list[ans.id].content = ans_str
    return self.chat_list[ans.id]
  
  # __func can't be exposed to frontend
  def __askquest_worker(self):
    while True:
      idx = self.quest_queue.get()
      qest = self.chat_list[idx].content
      stream = self.chain.stream(qest)
      for tok in stream:
        self.answer_queue.put(ChatInfo(id=idx, content=tok))
      self.answer_queue.put(ChatInfo(id=idx, content="<END>"))
  

# 模拟OpenAI的流式响应
def simulate_openai_stream() -> Generator[str]:
  markdown_content = """
# 流式Markdown演示

这是一个演示文本，将会逐字显示。

## 主要特点：
- 实时更新
- 平滑显示
- 支持Markdown格式

### 代码示例：
```python
def hello_world():
  print("Hello, World!")
```
  """

  for char in markdown_content:
    yield char
    time.sleep(0.1)


def main():
  # 创建初始HTML文件
  # html_file = viewer.create_temp_html()
  html_file = "html/dist/index.html"
  api = ChatBackendAPI()
  webview.create_window(
    "AI助手", html_file, 
    js_api=api,
    width=800, height=600
  )
  webview.start()

# server = fastapi.FastAPI()
# api = ChatBackendAPI()

# @server.post("/question")
# async def new_question(qest: str):
#   return api.add_or_update_question(-1, qest)

# @server.put("/question/{id}")
# async def update_question(id: int, qest: str):
#   assert api.chat_list[id].type == RoleName.You
#   return api.add_or_update_question(id, qest)

# @server.get("/answer")
# async def get_answer():
#   return api.get_answer()

if __name__ == "__main__":
  # is_dev = sys.argv[-1] == "dev"
  # if not is_dev:
  #   main()
  # uvicorn.run(server, host="localhost", port=8000)
  main()