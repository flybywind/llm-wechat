import platform
import pyperclip
from pynput import keyboard, mouse
import pyautogui
import time
import threading
from queue import Queue

# 创建一个队列来存储处理后的文本
text_queue = Queue()

# 全局变量
ctrl_pressed = False
c_pressed = False
last_copy_time = 0

CTRL_KEY = keyboard.Key.cmd if platform.system() == "Darwin" else keyboard.Key.ctrl


def process_clipboard():
    global last_copy_time
    # 等待一小段时间，确保剪贴板内容已更新
    time.sleep(0.1)
    # 获取剪贴板内容
    clipboard_content = pyperclip.paste()
    # 处理剪贴板内容 (这里只是一个简单的示例,您可以根据需要修改)
    processed_text = f"处理后的文本: {clipboard_content.upper()}"
    # 将处理后的文本放入队列
    text_queue.put(processed_text)
    print(f"检测到Ctrl+C,处理后的文本: {processed_text}")
    last_copy_time = time.time()


def on_press(key):
    global ctrl_pressed, c_pressed
    if key == CTRL_KEY:
        ctrl_pressed = True
    elif key == keyboard.KeyCode.from_char("c"):
        c_pressed = True

    if ctrl_pressed and c_pressed:
        # 在新线程中处理剪贴板内容
        threading.Thread(target=process_clipboard).start()


def on_release(key):
    global ctrl_pressed, c_pressed
    if key == CTRL_KEY:
        ctrl_pressed = False
    elif key == keyboard.KeyCode.from_char("c"):
        c_pressed = False


def on_click(x, y, button, pressed):
    global ctrl_pressed, last_copy_time
    if pressed and button == mouse.Button.left and ctrl_pressed:
        # 确保从上次复制到现在已经过了足够的时间
        if time.time() - last_copy_time > 0.5:
            # 尝试从队列中获取最新的处理后文本
            try:
                processed_text = text_queue.get_nowait()
                # 模拟键盘输入处理后的文本
                for c in processed_text:
                    pyautogui.typewrite(c, interval=0.1)
                print(f"已输入处理后的文本: {processed_text}")
            except Queue.Empty:
                print("队列为空，没有可用的处理后文本")
        else:
            print("请稍等片刻，确保剪贴板内容已更新")


# 设置键盘监听器
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
keyboard_listener.start()

# 设置鼠标监听器
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

print("Mac剪贴板助手已启动。按Ctrl+C复制文本,按Ctrl+鼠标左键粘贴处理后的文本。")

# 保持程序运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    keyboard_listener.stop()
    mouse_listener.stop()
    print("程序已退出。")
