from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal

STYLE_DIR = Path(__file__).parent
THEME_DIR = STYLE_DIR / "theme"


class ThemeManager(QObject):
    """Quản lý theme tập trung (light/dark)."""
    theme_changed = Signal(dict, str)  # (theme_data, theme_name)

    def __init__(self, theme: str = "light") -> None:
        super().__init__()
        self._theme_name = theme
        self._theme_data = self._load_theme(theme)

    def _load_theme(self, theme: str) -> dict:
        theme_file = THEME_DIR / f"theme_{theme}.json"
        return json.loads(theme_file.read_text(encoding="utf-8"))

    def get_theme_data(self) -> dict:
        return self._theme_data

    def get_theme_name(self) -> str:
        return self._theme_name

    def set_theme(self, theme: str) -> None:
        """Đổi theme và phát signal cho toàn app."""
        if theme != self._theme_name:
            self._theme_name = theme
            self._theme_data = self._load_theme(theme)
            self.theme_changed.emit(self._theme_data, self._theme_name)
