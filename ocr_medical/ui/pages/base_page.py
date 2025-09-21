from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.style.style_loader import load_theme_qss
from ui.style.theme_manager import ThemeManager

PAGE_QSS_MAP = {
    "HomePage": "home_page",
    "ExtraInfoPage": "extract_info_page",
    "FileLogPage": "file_log_page",
    "ReviewPage": "review_page",
    "SettingPage": "setting_page",
}


class BasePage(QWidget):
    def __init__(self, title: str, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setObjectName(f"Page__{title.replace(' ', '_')}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.header = QLabel(title)
        self.header.setObjectName("PageHeader")
        layout.addWidget(self.header)
        layout.addStretch(1)

        # lắng nghe sự kiện đổi theme
        self.theme_manager.theme_changed.connect(self.apply_theme)

        # áp theme ban đầu
        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name(),
        )

    def apply_theme(self, theme_data: dict, theme_name: str):
        class_name = self.__class__.__name__
        page_name = PAGE_QSS_MAP.get(class_name, None)

        if page_name:
            try:
                qss = load_theme_qss(theme_name, page_name)
                self.setStyleSheet(qss)
            except FileNotFoundError:
                # fallback: không crash nếu chưa có file qss riêng
                self.setStyleSheet("")
