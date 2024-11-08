import tkinter as tk
from tkinter import ttk
import platform


class SearchableSettingsDialog(tk.Toplevel):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager

        # 设置窗口标题和大小
        self.title("Settings")
        self.geometry("600x400")

        # 设置最小窗口大小
        self.minsize(500, 300)

        # 设置窗口样式
        if platform.system() == "Darwin":  # macOS
            try:
                self.tk.call(
                    "::tk::unsupported::MacWindowStyle",
                    "style",
                    self._w,
                    "moveableModal",
                    "",
                )
            except tk.TclError:
                pass  # 如果设置失败，继续使用默认样式

        # 添加ESC键关闭窗口
        self.bind("<Escape>", lambda e: self.destroy())

        # 添加搜索框占位符文本处理方法
        self.placeholder_text = "Search settings..."
        # 确定操作系统并设置适当的标题栏样式
        if platform.system() == "Darwin":  # macOS
            try:
                self.tk.call(
                    "::tk::unsupported::MacWindowStyle",
                    "style",
                    self._w,
                    "moveableModal",
                    "",
                )
            except tk.TclError:
                pass  # 如果设置失败，继续使用默认样式

        # 创建主框架
        self.create_widgets()

        # 使窗口成为模态
        self.transient(parent)
        self.grab_set()

        # 居中显示
        self.center_window()

        # 存储所有设置项的引用
        self.setting_frames = {}

        # 初始化设置项
        self.initialize_settings()

        # 绑定搜索框事件
        self.search_var.trace("w", self.filter_settings)

    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        # 设置样式
        style = ttk.Style()
        style.configure("Search.TFrame", background="#f0f0f0")

        # 创建主容器
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # 创建顶部栏（包含关闭按钮）
        top_bar = ttk.Frame(self.main_container)
        top_bar.pack(fill=tk.X, pady=(5, 0))

        # 添加设置标题
        ttk.Label(top_bar, text="Settings", font=("", 12, "bold")).pack(
            side=tk.LEFT, padx=10
        )

        # 创建搜索框区域（使用特殊样式）
        search_container = ttk.Frame(self.main_container, style="Search.TFrame")
        search_container.pack(fill=tk.X, pady=0)

        # 创建搜索框框架
        search_frame = ttk.Frame(search_container)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # 创建搜索图标标签（可以用 🔍 符号代替真实图标）
        ttk.Label(search_frame, text="🔍").pack(side=tk.LEFT, padx=(0, 5))

        # 创建搜索输入框
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, font=("", 10)
        )
        self.search_entry.pack(fill=tk.X, expand=True)
        self.search_entry.insert(0, "Search settings...")
        self.search_entry.bind("<FocusIn>", lambda e: self.on_search_focus_in())
        self.search_entry.bind("<FocusOut>", lambda e: self.on_search_focus_out())

        # 添加分隔线
        separator = ttk.Separator(self.main_container, orient="horizontal")
        separator.pack(fill=tk.X, pady=0)

        # 创建设置项的容器（带滚动条）
        self.canvas = tk.Canvas(self.main_container)
        scrollbar = ttk.Scrollbar(
            self.main_container, orient="vertical", command=self.canvas.yview
        )
        self.settings_frame = ttk.Frame(self.canvas)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 打包滚动条和画布
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建画布窗口
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.settings_frame, anchor="nw"
        )

        # 绑定画布和框架事件
        self.settings_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # 绑定鼠标滚轮事件（适配不同操作系统）
        if platform.system() == "Windows":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_windows)
        elif platform.system() == "Darwin":  # macOS
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_macos)
        else:  # Linux
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _on_mousewheel_windows(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_macos(self, event):
        self.canvas.yview_scroll(int(-1 * event.delta), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def on_frame_configure(self, event=None):
        """重置画布滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """当画布大小改变时，调整内部框架的大小"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def initialize_settings(self):
        """初始化所有设置项"""
        settings = [
            (
                "General",
                [
                    ("Bot Name", "bot_name", "text", "Name of the AI bot"),
                    (
                        "Theme",
                        "theme",
                        "combo",
                        ["Light", "Dark", "System"],
                        "Application theme",
                    ),
                ],
            ),
            (
                "API Settings",
                [
                    ("API Key", "api_key", "password", "Your API authentication key"),
                    ("API Endpoint", "api_endpoint", "text", "API server endpoint"),
                    (
                        "Max Tokens",
                        "max_tokens",
                        "number",
                        "Maximum tokens per response",
                    ),
                ],
            ),
            (
                "Chat Settings",
                [
                    (
                        "Message History",
                        "message_history",
                        "number",
                        "Number of messages to keep in history",
                    ),
                    (
                        "Auto Save",
                        "auto_save",
                        "boolean",
                        "Automatically save chat history",
                    ),
                    (
                        "Notification Sound",
                        "notification_sound",
                        "boolean",
                        "Play sound on new messages",
                    ),
                ],
            ),
        ]

        for section_name, section_settings in settings:
            # 创建分类标签
            section_frame = ttk.LabelFrame(self.settings_frame, text=section_name)
            section_frame.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)

            for setting_name, key, input_type, *args in section_settings:
                # 创建设置项框架
                setting_frame = ttk.Frame(section_frame)
                setting_frame.pack(fill=tk.X, padx=5, pady=2)

                # 创建标签
                ttk.Label(setting_frame, text=setting_name).pack(side=tk.LEFT)

                # 获取当前值
                current_value = self.config_manager.get_config(key, "")

                # 根据输入类型创建不同的输入控件
                if input_type == "text":
                    entry = ttk.Entry(setting_frame)
                    entry.insert(0, current_value)
                    entry.pack(side=tk.RIGHT, padx=5)

                elif input_type == "password":
                    entry = ttk.Entry(setting_frame, show="*")
                    entry.insert(0, current_value)
                    entry.pack(side=tk.RIGHT, padx=5)

                elif input_type == "number":
                    spinbox = ttk.Spinbox(setting_frame, from_=0, to=9999)
                    spinbox.set(current_value or 0)
                    spinbox.pack(side=tk.RIGHT, padx=5)

                elif input_type == "boolean":
                    var = tk.BooleanVar(value=bool(current_value))
                    checkbox = ttk.Checkbutton(setting_frame, variable=var)
                    checkbox.pack(side=tk.RIGHT, padx=5)

                elif input_type == "combo":
                    combo = ttk.Combobox(
                        setting_frame, values=args[0], state="readonly"
                    )
                    combo.set(current_value or args[0][0])
                    combo.pack(side=tk.RIGHT, padx=5)

                # 添加提示信息
                if len(args) > 0 and input_type != "combo":
                    tooltip = args[0]
                    setting_frame.tooltip = tooltip
                elif len(args) > 1:
                    tooltip = args[1]
                    setting_frame.tooltip = tooltip

                # 存储设置项引用
                self.setting_frames[key] = {
                    "frame": setting_frame,
                    "name": setting_name,
                    "section": section_name,
                }

    def filter_settings(self, *args):
        """根据搜索词过滤设置项"""
        search_text = self.search_var.get().lower()

        for key, setting_info in self.setting_frames.items():
            frame = setting_info["frame"]
            name = setting_info["name"]
            section = setting_info["section"]

            # 检查是否匹配搜索词
            if (
                search_text in name.lower()
                or search_text in key.lower()
                or search_text in section.lower()
                or hasattr(frame, "tooltip")
                and search_text in frame.tooltip.lower()
            ):
                frame.pack(fill=tk.X, padx=5, pady=2)
            else:
                frame.pack_forget()

    def on_search_focus_in(self):
        """当搜索框获得焦点时"""
        if self.search_entry.get() == self.placeholder_text:
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(foreground="black")

    def on_search_focus_out(self):
        """当搜索框失去焦点时"""
        if not self.search_entry.get():
            self.search_entry.insert(0, self.placeholder_text)
            self.search_entry.configure(foreground="gray")
