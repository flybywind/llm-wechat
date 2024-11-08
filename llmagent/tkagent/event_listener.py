from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
import sys
from threading import Timer
from loguru import logger
import platform
import pyperclip
from pynput import keyboard, mouse
import pyautogui
import time
from typing import Union
from queue import Queue, Empty as QueueEmptyException

from ..conf import config

CTRL_KEY = keyboard.Key.cmd if platform.system() == "Darwin" else keyboard.Key.ctrl
KeyEvent = namedtuple("KeyEvent", ["key", "time"])


class MonitorEvent:
    """
    监控的虚拟事件
    """

    def __init__(
        self,
        first_key: Union[keyboard.KeyCode, mouse.Button],
        second_key: Union[keyboard.KeyCode, mouse.Button],
    ) -> None:
        self.first_key = first_key
        self.second_key = second_key

    def hit(self, key: keyboard.KeyCode, last_event: KeyEvent) -> bool:
        return (
            last_event
            and key == self.second_key
            and last_event.key == self.first_key
            and time.time() - last_event.time < config.COMPOSE_KEY_INTERVAL
        )


Ctrl_C: MonitorEvent = MonitorEvent(
    first_key=CTRL_KEY, second_key=keyboard.KeyCode.from_char("c")
)
Double_Mouse_Left: MonitorEvent = MonitorEvent(
    first_key=mouse.Button.left, second_key=mouse.Button.left
)

Ctrl_Mouse_Left: MonitorEvent = MonitorEvent(
    first_key=CTRL_KEY, second_key=mouse.Button.left
)

class TimeoutQueue:
    def __init__(self, timeout:int = -1, maxsize: int = 0) -> None:
        self._queue = Queue(maxsize)
        self._timeout = timeout
        self._timer = None
        self._reset_timer()

    def get(self, block=True, timeout=1):
        return self._queue.get(block=block, timeout=timeout)

    def put(self, item, block: bool = True, timeout: float | None = None) -> None:
        self._reset_timer()
        return self._queue.put(item, block, timeout)
    
    def _make_empty(self):
        logger.info(f"timer tick hit after {self._timeout}s, make queue empty")
        self._queue = Queue()
    
    def _reset_timer(self):
        if self._timeout < 0: return
        if self._timer:
            self._timer.cancel()
            del self._timer
        self._timer = Timer(self._timeout, self._make_empty)
        self._timer.start()

class KeystrokeListener:
    text_queue = TimeoutQueue(60)
    text_queue_ai = Queue()
    keyevent_last: KeyEvent = None
    mouseevent_last: KeyEvent = None
    executor: ThreadPoolExecutor = ThreadPoolExecutor()
    last_text: str = ""

    keyboard_listener = None
    mouse_listener = None
    langchain = None

    def start(self):
        # 设置键盘监听器
        self.keyboard_listener = keyboard.Listener(on_press=self._keyboard_on_press)
        self.keyboard_listener.start()
        # 设置鼠标监听器
        self.mouse_listener = mouse.Listener(on_click=self._mouse_on_click)
        self.mouse_listener.start()
        return

    def set_langchain(self, langchain):
        self.langchain = langchain

    def _keyboard_on_press(self, key):
        if Ctrl_C.hit(key, self.keyevent_last):
            self.executor.submit(self._process_clipboard)
        self.keyevent_last = KeyEvent(key=key, time=time.time())

    def _mouse_on_click(self, x, y, button, pressed):
        if pressed and Ctrl_Mouse_Left.hit(button, self.keyevent_last) \
            and Double_Mouse_Left.hit(button, self.mouseevent_last):
            self.executor.submit(self._process_typewrite)
        self.mouseevent_last = KeyEvent(key=button, time=time.time())

    def _process_clipboard(self):
        for _ in range(10):
            # 等待一小段时间，确保剪贴板内容已更新
            time.sleep(0.1)
            clipboard_content = pyperclip.paste()
            if clipboard_content != self.last_text:
                break
        if clipboard_content == self.last_text:
            logger.warning("剪贴板内容未更新")
            return
        self.last_text = clipboard_content

        # 处理剪贴板内容 (这里只是一个简单的示例,您可以根据需要修改)
        if self.langchain:
            processed_text = self.langchain.stream(clipboard_content)
            # logger.info(f"检测到Ctrl+C,处理后的文本: {processed_text}")
            self.text_queue = TimeoutQueue(60)
            for c in processed_text:
                self.text_queue.put(c)
                self.text_queue_ai.put(c)
            self.text_queue_ai.put("<END>")
        else:
            logger.warning("未设置langchain, 无法处理剪贴板内容")

    def _process_typewrite(self):
        try:
            while True:
                pyautogui.typewrite(self.text_queue.get(timeout=1))
        except QueueEmptyException:
            pass
        except Exception as e:
            logger.exception(f"get buffered processed text timeout: {repr(e)}, return")
