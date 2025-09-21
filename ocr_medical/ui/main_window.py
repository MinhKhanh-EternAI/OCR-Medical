from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QStackedWidget, QFrame
)
from .widgets.side_panel import SidePanel
from .pages.home_page import HomePage
from .pages.setting_page import SettingPage
from .pages.file_log_page import FileLogPage
from .pages.extract_info_page import ExtraInfoPage
from .pages.review_page import ReviewPage
from .style.theme_manager import ThemeManager
from .style.style_loader import load_theme_qss

MARGIN = 24
GUTTER = 24
SIDE_COLS = 2
TOTAL_COLS = 12
MAIN_COLS = TOTAL_COLS - SIDE_COLS
TOTAL_ROWS = 12


class Panel(QFrame):
    """Khung panel có border/background đồng nhất theo theme."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path, theme_name: str = "light") -> None:
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle("OCR-Medical")

        # --- Theme Manager ---
        self.theme_manager = ThemeManager(theme_name)
        self.theme_manager.theme_changed.connect(self.apply_theme)

        # Central container
        root = QWidget(self)
        self.setObjectName("MainWindow")
        self.setCentralWidget(root)
        grid = QGridLayout(root)
        grid.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        grid.setHorizontalSpacing(GUTTER)
        grid.setVerticalSpacing(GUTTER)

        # Thiết lập 12 cột / 12 hàng theo tỉ lệ đều
        for c in range(TOTAL_COLS):
            grid.setColumnStretch(c, 1)
        for r in range(TOTAL_ROWS):
            grid.setRowStretch(r, 1)

        # --- Side Panel ---
        self.side_panel = SidePanel(
            project_root=self.project_root,
            theme_manager=self.theme_manager
        )
        side_wrapper = Panel()
        side_layout = QGridLayout(side_wrapper)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.addWidget(self.side_panel, 0, 0, 1, 1)

        # --- Main Stack (các page) ---
        self.stack = QStackedWidget()
        main_wrapper = Panel()
        main_layout = QGridLayout(main_wrapper)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack, 0, 0, 1, 1)

        # Thêm vào grid 12x12
        grid.addWidget(side_wrapper, 0, 0, TOTAL_ROWS, SIDE_COLS)
        grid.addWidget(main_wrapper, 0, SIDE_COLS, TOTAL_ROWS, MAIN_COLS)

        # Đăng ký các trang (truyền theme_manager vào từng page)
        self.page_index: dict[str, int] = {}
        self._add_page("home", HomePage(self.theme_manager))
        self._add_page("setting", SettingPage(self.theme_manager))
        self._add_page("file_log", FileLogPage(self.theme_manager))
        self._add_page("extra_info", ExtraInfoPage(self.theme_manager))
        self._add_page("review", ReviewPage(self.theme_manager))

        # Bắt sự kiện nav
        self.side_panel.page_selected.connect(self.navigate_to)

        # Mặc định vào Home
        self.navigate_to("home")

        # Áp style global lần đầu
        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name()
        )

    def _add_page(self, key: str, widget: QWidget) -> None:
        idx = self.stack.addWidget(widget)
        self.page_index[key] = idx

    def navigate_to(self, key: str) -> None:
        if key in self.page_index:
            self.stack.setCurrentIndex(self.page_index[key])
            self.side_panel.set_active(key)

    def apply_theme(self, theme_data: dict, theme_name: str) -> None:
        qss = load_theme_qss(theme_name)   # global style
        self.setStyleSheet(qss)
