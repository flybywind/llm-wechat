from datetime import datetime
from enum import Enum
from loguru import logger
import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLLabel
import markdown


class Role(Enum):
    AI = "ai"
    USER = "user"


class ChatFrame:
    def __init__(self, parent) -> None:
        self.root = parent
        # 创建聊天显示区域
        self.chat_frame = ttk.Frame(self.root)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建聊天历史显示
        self.chat_markdown = HTMLLabel(
            self.chat_frame,
            background="#ffffff",
            html="<body style='background-color: #ffffff;'></body>",
            pady=10,
            padx=10,
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

        # html样式
        self._html_chat_content = []
        self._user_style = """
        <div style="padding-left: 20px; " >
            <div style="background-color:#eeeedd; padding: 5px; border-radius:0.5rem">
            [{timestamp}] <br/>
            你: <br/>
            <div>
                {chat}
            </div>
            </div>
        </div>
        """
        self._ai_style = """
        <div style="padding-right: 20px; margin: 10px 0 " >
            <div style="background-color:#eeeeee; padding: 5px; border-radius:0.5rem">
            [{timestamp}] <br/>
            AI:<br/>
            <div>
                {chat}
            </div>
	    </div>
        </div>
        """

    def send_message(self, event):
        # 获取用户的输入的文本
        message = self.input_entry.get().strip()
        if message:
            # 更新显示
            self.update_chat_display(message, Role.USER)
            # 清空输入框
            self.input_entry.delete(0, tk.END)

    def update_chat_display(self, message, role):
        # 获取当前时间
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_msg = markdown.markdown(message)
        # 根据角色选择样式
        if role == Role.USER:
            chat_content = self._user_style.format(timestamp=timestamp, chat=html_msg)
        else:
            chat_content = self._ai_style.format(timestamp=timestamp, chat=html_msg)
        self._html_chat_content.append(chat_content)

        full_chat_html = "\n".join(self._html_chat_content)
        # 设置完整的HTML内容
        full_html = f"""
        <body style="background-color: #ffffff; font-family: Arial, sans-serif;">
            {full_chat_html}
        </body>
        """
        # 更新显示
        self.chat_markdown.set_html(full_html)
        self.chat_markdown.see(tk.END)

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
