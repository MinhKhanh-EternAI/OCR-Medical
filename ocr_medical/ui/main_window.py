from __future__ import annotations
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QStackedWidget, QFrame

from pathlib import Path

from ocr_medical.ui.widgets.side_panel import SidePanel
from ocr_medical.ui.pages.home_page import HomePage
from ocr_medical.ui.pages.setting_page import SettingPage
from ocr_medical.ui.pages.file_log_page import FileLogPage
from ocr_medical.ui.pages.extract_info_page import ExtraInfoPage
from ocr_medical.ui.pages.review_page import ReviewPage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_theme_qss


MARGIN = 24
GUTTER = 24
SIDE_COLS = 2
TOTAL_COLS = 12
MAIN_COLS = TOTAL_COLS - SIDE_COLS
TOTAL_ROWS = 12


class Panel(QFrame):
    """Khung panel có border / nền đồng nhất theo theme."""

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

        logo_path = self.project_root / "assets" / "logo" / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self.theme_manager = ThemeManager(theme_name)
        self.theme_manager.theme_changed.connect(self.apply_theme)

        root = QWidget(self)
        self.setObjectName("MainWindow")
        self.setCentralWidget(root)

        grid = QGridLayout(root)
        grid.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        grid.setHorizontalSpacing(GUTTER)
        grid.setVerticalSpacing(GUTTER)

        for c in range(TOTAL_COLS):
            grid.setColumnStretch(c, 1)
        for r in range(TOTAL_ROWS):
            grid.setRowStretch(r, 1)

        self.side_panel = SidePanel(
            project_root=self.project_root,
            theme_manager=self.theme_manager
        )
        side_wrapper = Panel()
        from PySide6.QtWidgets import QGridLayout as QGL
        side_layout = QGL(side_wrapper)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.addWidget(self.side_panel, 0, 0, 1, 1)

        self.stack = QStackedWidget()
        main_wrapper = Panel()
        main_layout = QGL(main_wrapper)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack, 0, 0, 1, 1)

        grid.addWidget(side_wrapper, 0, 0, TOTAL_ROWS, SIDE_COLS)
        grid.addWidget(main_wrapper, 0, SIDE_COLS, TOTAL_ROWS, MAIN_COLS)

        self.page_index: dict[str, int] = {}

        home_page = HomePage(self.theme_manager)
        home_page.process_requested.connect(self._go_to_extract_info)
        self._add_page("home", home_page)

        self._add_page("setting", SettingPage(self.theme_manager))
        self._add_page("file_log", FileLogPage(self.theme_manager))

        extract_page = ExtraInfoPage(self.theme_manager)
        extract_page.navigate_back_requested.connect(
            lambda: self.navigate_to("home"))
        self._add_page("extra_info", extract_page)

        self._add_page("review", ReviewPage(self.theme_manager))

        self.side_panel.page_selected.connect(self.navigate_to)

        self.navigate_to("home")

        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name()
        )

    def disable_focus_policy(self):
        """Disable focus policy cho toàn bộ ứng dụng"""
        self.set_focus_policy_recursive(self, Qt.NoFocus)

    @staticmethod
    def set_focus_policy_recursive(widget, policy):
        """Recursively set focus policy cho tất cả children"""
        widget.setFocusPolicy(policy)
        for child in widget.findChildren(QWidget):
            child.setFocusPolicy(policy)

    def _add_page(self, key: str, widget: QWidget) -> None:
        idx = self.stack.addWidget(widget)
        self.page_index[key] = idx

    def navigate_to(self, key: str) -> None:
        if key in self.page_index:
            self.stack.setCurrentIndex(self.page_index[key])
            self.side_panel.set_active(key)

    def _go_to_extract_info(self, files: list[Path]):
        self.navigate_to("extra_info")

        page = self.stack.widget(self.page_index["extra_info"])
        if hasattr(page, "load_files"):
            page.load_files(files)

    def apply_theme(self, theme_data: dict, theme_name: str) -> None:
        qss = load_theme_qss(theme_name)
        self.setStyleSheet(qss)
