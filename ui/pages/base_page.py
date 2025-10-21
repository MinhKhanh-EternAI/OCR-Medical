from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from ui.style.style_loader import load_theme_qss
from ui.style.theme_manager import ThemeManager


# Map tên class của page với tên file QSS tương ứng
PAGE_QSS_MAP = {
    "HomePage": "home_page",
    "ExtraInfoPage": "extract_info_page",
    "FileLogPage": "file_log_page",
    "ReviewPage": "review_page",
    "SettingPage": "setting_page",
}


class BasePage(QWidget):
    """
    Class cơ sở cho tất cả các trang trong ứng dụng.
    Cung cấp cấu trúc chung: header, divider và hỗ trợ theme động.
    """
    def __init__(self, title: str, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__(parent)
        self.theme_manager = theme_manager
        
        # Đặt object name để dễ dàng styling bằng QSS
        self.setObjectName(f"Page__{title.replace(' ', '_')}")

        # Tạo layout chính với margin và spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- Header: Tiêu đề trang ---
        self.header = QLabel(title)
        self.header.setObjectName("PageHeader")
        layout.addWidget(self.header)

        # --- Divider: Đường phân cách ngang ---
        self.divider = QFrame()
        self.divider.setObjectName("Divider")
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(self.divider)

        # Lắng nghe sự kiện đổi theme để cập nhật giao diện
        self.theme_manager.theme_changed.connect(self.apply_theme)

        # Áp dụng theme ban đầu
        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name(),
        )

    def apply_theme(self, theme_data: dict, theme_name: str):
        """
        Áp dụng theme cho page.
        Tự động load file QSS tương ứng dựa vào tên class.
        """
        class_name = self.__class__.__name__
        page_name = PAGE_QSS_MAP.get(class_name, None)

        if page_name:
            try:
                # Load file QSS từ theme hiện tại
                qss = load_theme_qss(theme_name, page_name)
                self.setStyleSheet(qss)
            except FileNotFoundError:
                # Nếu không tìm thấy file QSS, xóa stylesheet
                self.setStyleSheet("")