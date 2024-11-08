import sys
from time import sleep
import tkinter as tk
import platform
import traceback
from loguru import logger

from .conf_manager import ConfigManager
from .setting_dialog import SearchableSettingsDialog
from .chat_frame import ChatFrame
from .event_listener import KeystrokeListener

class ChatApp:
    def __init__(self, root, listener: KeystrokeListener):
        self.root = root
        self.root.title("Chat Application")
        self.listener_for_langchain = listener
        self.text_queue_ai = listener.text_queue_ai
        self.config_manager = ConfigManager()

        # 设置主窗口大小
        self.root.geometry("800x600")

        # 创建主界面
        self.create_widgets()

        # 绑定快捷键
        self.bind_shortcuts()
        
        self.update_langchain()

    def update_langchain(self):
        langchain = self.config_manager.get_langchain_or_default()
        self.listener_for_langchain.set_langchain(langchain)

    def bind_shortcuts(self):
        """绑定全局快捷键"""
        system = platform.system()
        if system == "Darwin":  # macOS
            self.root.bind("<Command-,>", self.open_settings)
        else:  # Windows/Linux
            self.root.bind("<Control-,>", self.open_settings)

    def open_settings(self, event=None):
        """打开设置窗口"""
        SearchableSettingsDialog(self.root, self.config_manager)
        # 每次都检查一下langchain是否有变化，并重置一下
        self.update_langchain()

    def create_widgets(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 添加设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(
            label="Preferences",
            command=self.open_settings,
            accelerator="Cmd+," if platform.system() == "Darwin" else "Ctrl+,",
        )

        # 创建聊天显示区域
        self.chat_frame = ChatFrame(self.root, self.text_queue_ai)
        # 创建demo输入
        # self.chat_frame.add_demo_messages()


def start_keystroke_event_listener():

    keystroke_listener = KeystrokeListener()
    keystroke_listener.start()
    return keystroke_listener

def create_app(listener):
    try:
        root = tk.Tk()
        app = ChatApp(root, listener)
        root.mainloop()
        # sleep(10)
    except Exception as e:
        logger.exception("Error in create_app:", e)
        raise

def main():
    try:
        from ..conf import config

        logger.remove()
        logger.add(
            sys.stdout,
            level=config.LOG_LEVEL,
            enqueue=True,
        )

        listener = start_keystroke_event_listener()
        create_app(listener)
    except Exception as e:
        logger.exception(e) 

