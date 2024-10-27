import tkinter as tk
import platform

from .conf_manager import ConfigManager
from .setting_dialog import SearchableSettingsDialog
from .chat_frame import ChatFrame

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")
        self.config_manager = ConfigManager()

        # 设置主窗口大小
        self.root.geometry("800x600")

        # 创建主界面
        self.create_widgets()

        # 绑定快捷键
        self.bind_shortcuts()

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
        self.chat_frame = ChatFrame(self.root)
        # 创建demo输入
        self.chat_frame.add_demo_messages()

def main():
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
