import subprocess
import sys
import time
from pathlib import Path
from threading import Timer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --------- Cấu hình ----------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = PROJECT_ROOT / "ocr_medical" / "ui"
MAIN_MODULE = "ocr_medical.main"     # ✅ chạy app theo dạng module để tránh lỗi import
DEBOUNCE_DELAY = 1.0                 # giây chờ sau lần thay đổi cuối cùng

process = None      # tiến trình app hiện tại
reload_timer = None # timer debounce


# --------- Watchdog Handler ----------
class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global reload_timer

        if event.is_directory:
            return

        path = Path(event.src_path)
        if str(UI_DIR) in str(path) or path.suffix in (".py", ".qss"):
            print(f"📂 Change detected: {path.name}")

            # Huỷ timer cũ và tạo timer mới (debounce)
            if reload_timer:
                reload_timer.cancel()
            reload_timer = Timer(DEBOUNCE_DELAY, restart_app)
            reload_timer.start()


# --------- App Control ----------
def start_app():
    """Chạy app theo module (-m ocr_medical.main)."""
    global process
    if process:
        process.kill()

    print("🚀 Starting app...")
    # ✅ dùng -m để Python hiểu ocr_medical là package
    process = subprocess.Popen([sys.executable, "-m", MAIN_MODULE])
    return process


def restart_app():
    """Kill app cũ và mở lại."""
    global process
    if process:
        print("💀 Restarting app...")
        process.kill()
        process.wait()
    start_app()


# --------- Main Entry ----------
if __name__ == "__main__":
    print("👀 Watch mode started.")
    print(f"📁 Watching directory: {UI_DIR}")

    # Khởi động lần đầu
    start_app()

    # Thiết lập Watchdog
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, str(UI_DIR), recursive=True)
    observer.schedule(event_handler, str(PROJECT_ROOT / "ocr_medical"), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping watcher...")
        observer.stop()
        if process:
            process.kill()

    observer.join()
