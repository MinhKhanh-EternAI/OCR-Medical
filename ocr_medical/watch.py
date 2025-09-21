import subprocess
import sys
import time
from pathlib import Path
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = PROJECT_ROOT / "ocr_medical" / "ui"
MAIN_FILE = PROJECT_ROOT / "ocr_medical" / "main.py"

process = None      # tiến trình app hiện tại
reload_timer = None # timer debounce
DEBOUNCE_DELAY = 1.0  # giây chờ sau lần thay đổi cuối cùng


class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global reload_timer

        if event.is_directory:
            return

        path = Path(event.src_path)
        if str(UI_DIR) in str(path) or path.samefile(MAIN_FILE):
            print(f"📂 Change detected: {path}")

            # Hủy timer cũ (nếu có) và tạo timer mới
            if reload_timer:
                reload_timer.cancel()
            reload_timer = Timer(DEBOUNCE_DELAY, restart_app)
            reload_timer.start()


def start_app():
    """Mở app mới"""
    global process
    if process:
        process.kill()
    print("🚀 Starting app...")
    process = subprocess.Popen([sys.executable, str(MAIN_FILE)])
    return process


def restart_app():
    """Kill app cũ và mở app mới"""
    global process
    if process:
        print("💀 Killing old app...")
        process.kill()
        process.wait()
    start_app()


if __name__ == "__main__":
    # Khởi động lần đầu
    start_app()

    # Watchdog
    event_handler = ReloadHandler()
    observer = Observer()

    observer.schedule(event_handler, str(UI_DIR), recursive=True)
    observer.schedule(event_handler, str(MAIN_FILE.parent), recursive=False)

    observer.start()
    print(f"👀 Watching UI dir: {UI_DIR}")
    print(f"👀 Watching main file: {MAIN_FILE}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping watcher...")
        observer.stop()
        if process:
            process.kill()

    observer.join()
