from __future__ import annotations
import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from ui.main_window import MainWindow

CONFIG_FILE = Path(__file__).resolve().parent / "config" / "app_config.json"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(data: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    app = QApplication(sys.argv)
    project_root = Path(__file__).resolve().parent
    config = load_config()
    theme_name = config.get("theme", "light")

    win = MainWindow(project_root, theme_name)

    screens = QGuiApplication.screens()
    idx = min(config.get("last_screen", 0), len(screens) - 1)
    geom = config.get("geometry")
    if geom:
        x, y, w, h = geom
        win.setGeometry(x, y, w, h)
    else:
        win.setGeometry(screens[idx].geometry())

    if config.get("is_fullscreen"):
        win.showFullScreen()
    elif config.get("is_maximized"):
        win.showMaximized()
    else:
        win.show()

    def on_quit():
        screen = win.windowHandle().screen()
        idx = screens.index(screen) if screen in screens else 0

        # Đọc config hiện có để merge
        existing = load_config()

        # Cập nhật thông tin cửa sổ, giữ nguyên phần khác
        existing.update({
            "last_screen": idx,
            "geometry": [
                win.geometry().x(),
                win.geometry().y(),
                win.geometry().width(),
                win.geometry().height()
            ],
            "is_maximized": win.isMaximized(),
            "is_fullscreen": win.isFullScreen(),
            "theme": win.theme_manager.get_theme_name(),
        })

        save_config(existing)

    app.aboutToQuit.connect(on_quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
