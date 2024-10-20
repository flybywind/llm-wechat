from collections import namedtuple
import sys
from loguru import logger
import platform
import pyperclip
from pynput import keyboard, mouse
import pyautogui
import time
import threading
from pydantic import BaseModel, Field
from queue import Queue

# 创建一个队列来存储处理后的文本
text_queue = Queue()
keystroke_queue = Queue()
CTRL_KEY = keyboard.Key.cmd if platform.system() == "Darwin" else keyboard.Key.ctrl

KeyEvent = namedtuple("KeyEvent", ["key", "time"])


class MonitorEvent(BaseModel):
    """
    监控的虚拟事件
    """

    compose_key: keyboard.KeyCode
    char_key: keyboard.KeyCode

    def hit(self, key: keyboard.KeyCode, last_event: KeyEvent, interval: float) -> bool:
        return (
            key == self.char_key
            and last_event.key == self.compose_key
            and time.time() - last_event.time < interval
        )


Ctrl_C: MonitorEvent = MonitorEvent(
    compose_key=CTRL_KEY, char_key=keyboard.KeyCode.from_char("c")
)


class KeystrokeListener(BaseModel):
    keystroke_queue = Queue()
    text_queue = Queue()
    compose_key_interval: int = Field(1, ge=0.1)
    keyevent_last: KeyEvent = None
    last_text: str = ""

    keyboard_listener = None
    mouse_listener = None

    def start(self):
        # 设置键盘监听器
        self.keyboard_listener = keyboard.Listener(on_press=self._keyboard_on_press)
        self.keyboard_listener.start()
        # 设置鼠标监听器
        self.mouse_listener = mouse.Listener(on_click=self._mouse_on_click)
        self.mouse_listener.start()

        threading.Thread(target=self._listener_task, daemon=True).start()
        return

    def _keyboard_on_press(self, key):
        self.keystroke_queue.put(key)

    def _mouse_on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            # wait for the ctrl key to be pressed
            try:
                key = self.keystroke_queue.get(timeout=self.compose_key_interval)
                if key == CTRL_KEY:
                    try:
                        while True:
                            processed_text = text_queue.get(timeout=1)
                            pyautogui.typewrite(processed_text)
                    except Exception as e:
                        logger.info(f"get buffered processed text timeout: {e}, return")
            except Exception as e:
                logger.exception(f"get keystroke key failed: {e}")

    def _listener_task(self):
        """
        监听所有按键信息，包括键盘和鼠标
        """
        while True:
            key = self.keystroke_queue.get()
            if Ctrl_C.hit(key, self.keyevent_last, self.compose_key_interval):
                ## Ctrl+C 事件
                self._process_clipboard()

            self.keyevent_last = KeyEvent(key=key, time=time.time())

    def _process_clipboard(self):
        for _ in range(10):
            # 等待一小段时间，确保剪贴板内容已更新
            time.sleep(0.1)
            clipboard_content = pyperclip.paste()
            if clipboard_content != self.last_text:
                break
        if clipboard_content == self.last_text:
            logger.info("剪贴板内容未更新")
            return
        self.last_text = clipboard_content

        # 处理剪贴板内容 (这里只是一个简单的示例,您可以根据需要修改)
        processed_text = clipboard_content.upper()
        logger.info(f"检测到Ctrl+C,处理后的文本: {processed_text}")
        # 将处理后的文本放入队列
        for c in processed_text:
            # 模拟流式处理
            self.text_queue.put(c)
            time.sleep(0.1)


print("Mac剪贴板助手已启动。按Ctrl+C复制文本,按Ctrl+鼠标左键粘贴处理后的文本。")


def main(log_level: str = "INFO"):
    logger.remove()
    logger.add(
        sys.stdout,
        level=log_level,
        enqueue=True,
    )

    keystroke_listener = KeystrokeListener()
    keystroke_listener.start()

    pending_forever = threading.Event()
    try:
        # 保持程序运行
        pending_forever.wait()
    except KeyboardInterrupt:
        logger.info("程序已退出。")


if __name__ == "__main__":
    import fire

    fire.Fire(main)
