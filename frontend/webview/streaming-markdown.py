import webview
import markdown
import threading
import asyncio
import tempfile
import time
import queue
from typing import Generator

from loguru import logger


class StreamingMarkdownViewer:
    def __init__(self):
        self.md = markdown.Markdown(extensions=["extra"])
        self.window = None
        self.temp_file = None
        self.content = ""
        self.update_queue = queue.Queue()
        self.is_running = True

    def create_html_template(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: #495483;
                    color: #ffffff;
                }
                pre {
                    background-color: #2d2d2d;
                    padding: 10px;
                    border-radius: 4px;
                }
                code {
                    background-color: #2d2d2d;
                    padding: 2px 4px;
                    border-radius: 4px;
                }
                .cursor {
                    display: inline-block;
                    width: 8px;
                    height: 16px;
                    background-color: #ffffff;
                    animation: blink 1s infinite;
                }
                @keyframes blink {
                    0% { opacity: 1; }
                    50% { opacity: 0; }
                    100% { opacity: 1; }
                }
            </style>
            <script>
                function updateContent(content) {
                    const mainContent = document.getElementById('content');
                    mainContent.innerHTML = content + '<span class="cursor"></span>';
                    window.scrollTo(0, document.body.scrollHeight);
                }
            </script>
        </head>
        <body>
            <div id="content"></div>
        </body>
        </html>
        """

    def create_temp_html(self):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
            f.write(self.create_html_template())
            self.temp_file = f.name
        return self.temp_file

    def update_content(self, new_content: str):
        """更新内容并通知WebView刷新"""
        self.content += new_content
        html_content = self.md.convert(self.content)
        if self.window:
            try:
                script = f"updateContent(`{html_content}`)"
                self.window.evaluate_js(script)
            except Exception as e:
                logger.warning(f"Error updating content: {e}, skipping update")

    async def process_stream(self):
        """处理更新队列中的内容"""
        while self.is_running:
            try:
                # todo 在处理到一半的时候，会出现格式问题。
                while not self.update_queue.empty():
                    new_content = self.update_queue.get_nowait()
                    self.update_content(new_content)
                await asyncio.sleep(0.05)  # 控制更新频率
            except Exception as e:
                logger.exception(f"Error processing stream: {e}")

    def add_content(self, content: str):
        """添加新内容到队列"""
        self.update_queue.put(content)


# 模拟OpenAI的流式响应
def simulate_openai_stream() -> Generator[str, None, None]:
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
    viewer = StreamingMarkdownViewer()

    # 创建初始HTML文件
    # html_file = viewer.create_temp_html()
    html_file = "html/dist/index.html"
    def start_streaming(viewer: StreamingMarkdownViewer):
        # 模拟从API获取流式响应
        for chunk in simulate_openai_stream():
            viewer.add_content(chunk)

    def start_asyncio_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(viewer.process_stream())

    # 启动后台处理线程
    threading.Thread(target=start_asyncio_loop, daemon=True).start()

    viewer.window = webview.create_window(
        "Markdown Preview", html_file, width=800, height=600
    )
    webview.start(start_streaming, viewer)


if __name__ == "__main__":
    main()
