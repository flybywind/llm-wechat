import os
import signal
import threading
import watchfiles
import subprocess
from loguru import logger

cur_dir = os.path.dirname(os.path.abspath(__file__))
backend_py = os.path.join(cur_dir, "backend.py")
app_root = os.path.abspath(os.path.join(cur_dir, ".."))
html_root = os.path.join(app_root, "webview/dist")


def restart_backend(pid):
    if pid > 0:
        logger.info("Killing backend process with pid: {}", pid)
        os.system("pkill -P {}".format(pid))

    pid = subprocess.Popen(
        "cd {} && python backend.py dev".format(cur_dir), shell=True
    ).pid

    logger.info("Backend process started with pid: {}", pid)
    return pid


def watch_and_reload(pid, event):
    logger.info("Watching for changes in {}", backend_py)
    for change in watchfiles.watch(backend_py, stop_event=event, debug=True):
        ## i couldn't get window.load_url() to actually work so I used this instead
        pid = restart_backend(pid)


if __name__ == "__main__":
    event = threading.Event()
    pid = restart_backend(-1)
    try:
        watch_and_reload(pid, event)
    except KeyboardInterrupt:
        event.set()

    logger.info("program closed, stopping watcher")
