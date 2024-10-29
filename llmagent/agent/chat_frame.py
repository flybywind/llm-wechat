from datetime import datetime
from enum import Enum
from queue import Queue
import threading
from typing import List, TypedDict, Union
from loguru import logger
import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLText
import markdown 


class Role(Enum):
    AI = "ai"
    USER = "user"
    PlaceHolder = "placeholder"

class HtmlMessage(TypedDict):
    role: Role
    timestamp: str
    chat: str

class HtmlMessageList:
    _user_style = """
        <div style="padding-left: 20px; " >
            <div style="background-color:#eeeedd; padding: 5px; border-radius:0.5rem">
            [{timestamp}] <br/>
            你: <br/>
            <div>
                {markdown}
            </div>
            </div>
        </div>
        """
    _ai_style = """
        <div style="padding-right: 20px; margin: 10px 0 " >
            <div style="background-color:#eeeeee; padding: 5px; border-radius:0.5rem">
            [{timestamp}] <br/>
            AI:<br/>
            <div>
                {markdown}
            </div>
	    </div>
        </div>
        """
    def __init__(self) -> None:
        self._messages: List[HtmlMessage] = []
        self._html_messages: List[str] = []
    
    def append(self, msg:HtmlMessage):
        self._messages.append(msg)
        if msg["role"] == Role.AI:
            self._html_messages.append(self._ai_style.format(timestamp=msg['timestamp'], 
                                                             markdown=markdown.markdown(msg['chat'])))
        elif msg["role"] == Role.USER:
            self._html_messages.append(self._user_style.format(timestamp = msg['timestamp'],
                                                               markdown=markdown.markdown(msg['chat'])))
    
    def pop(self, index=-1)->HtmlMessage:
        ai_start_msg = HtmlMessage(
            role=Role.AI,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), chat="")
        last_msg = ai_start_msg
        if len(self) > 0:
            last_msg = self._messages.pop(index)
            if last_msg["role"] == Role.AI:
                self._html_messages.pop(index)

        if last_msg["role"] == Role.AI:
            return last_msg
        elif last_msg["role"] == Role.USER:
            self._messages.append(last_msg)
        
        return ai_start_msg

         
    def __len__(self):
        assert len(self._messages) == len(self._html_messages), "length of raw messages and html messages should be the same"
        return len(self._messages)
    
    def __str__(self):
        self._messages = [msg for msg in self._messages if msg["role"]!=Role.PlaceHolder]
        return "\n".join(self._html_messages)
    
class ChatFrame:
    def __init__(self, parent, queue:Queue) -> None:
        self.root = parent
        self.text_queue_ai = queue
        # 创建聊天显示区域
        self.chat_frame = ttk.Frame(self.root)
    
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建聊天历史显示
        self.chat_markdown = HTMLText(
            self.chat_frame,
            background="#ffffff",
            html="<body style='background-color: #ffffff;'></body>",
            pady=0,
            padx=0,
            wrap=tk.WORD,
        )
        self.chat_markdown.pack(fill=tk.BOTH, expand=True)

        # 配置滚动条
        self.chat_markdown.vbar.configure(command=self.chat_markdown.yview)
        self.chat_markdown.pack(fill=tk.BOTH, expand=True)

        # 创建输入区域
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.input_entry = ttk.Entry(self.input_frame)
        self.input_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)

        self.send_button = ttk.Button(
            self.input_frame, text="Send", command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=5)

        # 绑定回车发送消息
        self.input_entry.bind("<Control-Return>", self.send_message)

        self.start_ai_responding_listenr()
        # html样式
        self._html_chat_content = HtmlMessageList()
        

    def send_message(self, event):
        # 获取用户的输入的文本
        message = self.input_entry.get().strip()
        if message:
            # 更新显示
            self.update_chat_display(message, Role.USER)
            # 清空输入框
            self.input_entry.delete(0, tk.END)

    def update_chat_display(self, message: Union[str, HtmlMessage], role):
        # 获取当前时间
        if isinstance(message, str):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg_body = HtmlMessage(timestamp=timestamp, chat=message, role=role)
        else:
            msg_body = message    
        self._html_chat_content.append(msg_body)

        # 设置完整的HTML内容
        full_html = f"""
        <body style="background-color: #ffffff; font-family: Arial, sans-serif;">
            {self._html_chat_content}
        </body>
        """
        # 更新显示
        self.chat_markdown.set_html(full_html)
        self.chat_markdown.see(tk.END)
    
    def start_ai_responding_listenr(self):
        def _listen_ai_responding():
            while True:
                try:
                    token = self.text_queue_ai.get()
                    if token == "<END>":
                        self._html_chat_content.append(HtmlMessage(role=Role.PlaceHolder))
                        continue
                    message = self._html_chat_content.pop()
                    message["chat"] += token
                    self.update_chat_display(message, Role.AI)
                except Exception as e:
                    logger.exception(e)

        threading.Thread(target=_listen_ai_responding).start()

    def add_demo_messages(self):
        # 添加一些示例消息，展示Markdown格式的支持
        example_messages = [
            "# Welcome to Markdown Chat!",
            """Here are some formatting examples:
- **Bold text**
- *Italic text*
- ~~Strikethrough~~""",
            """### Code Example
```python
def hello_world():
    print("Hello, World!")
```""",
            "> This is a blockquote message",
            """#### Table Example
| Name | Age |
|------|-----|
| John | 25  |
| Jane | 24  |""",
        ]
        for msg in example_messages:
            self.update_chat_display(msg, Role.AI)
        self.chat_markdown.see(tk.END)
