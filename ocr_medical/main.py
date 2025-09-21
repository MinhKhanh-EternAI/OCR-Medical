from __future__ import annotations
import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from ui.main_window import MainWindow

# File lưu cấu hình app (màn hình, kích thước, trạng thái, theme, ...)
CONFIG_FILE = Path(__file__).resolve().parent / "app_config.json"


def load_config() -> dict:
    """Đọc config từ file"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(data: dict) -> None:
    """Ghi config ra file"""
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    app = QApplication(sys.argv)

    project_root = Path(__file__).resolve().parent
    win = MainWindow(project_root=project_root)

    screens = QGuiApplication.screens()
    config = load_config()

    # --- Khôi phục màn hình và trạng thái ---
    target_index = config.get("last_screen", 0)
    geom = config.get("geometry", None)
    is_maximized = config.get("is_maximized", False)
    is_fullscreen = config.get("is_fullscreen", False)

    if 0 <= target_index < len(screens):
        if geom:
            # Nếu có geometry thì set theo geometry đã lưu
            try:
                x, y, w, h = geom
                win.setGeometry(x, y, w, h)
            except Exception:
                win.setGeometry(screens[target_index].geometry())
        else:
            # Nếu chưa có geometry thì cho vào giữa màn hình target
            win.setGeometry(screens[target_index].geometry())

    # Hiển thị theo trạng thái đã lưu
    if is_fullscreen:
        win.showFullScreen()
    elif is_maximized:
        win.showMaximized()
    else:
        win.show()

    # --- Lưu lại khi app đóng ---
    def on_about_to_quit():
        screen = win.windowHandle().screen()
        if screen in screens:
            idx = screens.index(screen)
        else:
            idx = 0

        data = {
            "last_screen": idx,
            "geometry": [
                win.geometry().x(),
                win.geometry().y(),
                win.geometry().width(),
                win.geometry().height()
            ],
            "is_maximized": win.isMaximized(),
            "is_fullscreen": win.isFullScreen(),
        }
        save_config(data)

    app.aboutToQuit.connect(on_about_to_quit)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
