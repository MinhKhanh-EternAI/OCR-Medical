from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer


STYLE_DIR = Path(__file__).parent
THEME_DIR = STYLE_DIR / "theme"
PAGES_DIR = STYLE_DIR / "pages"


def load_theme_qss(theme: str = "light", page: str | None = None) -> str:
    """Render QSS từ template + theme JSON."""
    theme_file = THEME_DIR / f"theme_{theme}.json"
    theme_data = json.loads(theme_file.read_text(encoding="utf-8"))

    if page:
        tpl_file = PAGES_DIR / f"{page}.qss.tpl"
    else:
        tpl_file = STYLE_DIR / "pages" / "style.qss.tpl"

    template = tpl_file.read_text(encoding="utf-8")

    def deep_format(s: str, ctx: dict, prefix="") -> str:
        out = s
        for k, v in ctx.items():
            if isinstance(v, dict):
                out = deep_format(out, v, f"{prefix}{k}.")
            else:
                out = out.replace(f"{{{{ {prefix}{k} }}}}", str(v))
        return out

    return deep_format(template, theme_data)


def load_theme_data(theme: str = "light") -> dict:
    """Load raw theme JSON (dùng trong code Python)."""
    THEME_DIR = STYLE_DIR / "theme"
    theme_file = THEME_DIR / f"theme_{theme}.json"
    return json.loads(theme_file.read_text(encoding="utf-8"))


def load_svg_colored(path: Path, color: str, size: int = 20) -> QIcon:
    """Load SVG và tô lại bằng màu theme"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    renderer = QSvgRenderer(str(path))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()

    return QIcon(pixmap)
