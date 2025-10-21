from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QPushButton

from ui.style.style_loader import load_svg_colored
from ui.style.theme_manager import ThemeManager
from utils.path_helper import resource_path


# ============================================================
#                     NavButton
# ============================================================
class NavButton(QWidget):
    """Custom nav button với icon đổi màu theo trạng thái"""

    def __init__(self, key: str, text: str, icon_path: Path, theme_data: dict, parent=None):
        super().__init__(parent)

        # Tạo QPushButton
        self.btn = QPushButton(f"  {text}", self)
        self.btn.setObjectName(f"NavBtn__{key}")
        self.btn.setProperty("nav", True)
        self.btn.setCheckable(True)
        self.btn.setAutoExclusive(True)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Lưu thông tin
        self.icon_path = icon_path
        self.normal_color = theme_data["color"]["text"]["primary"]
        self.hover_color = theme_data["color"]["text"]["primary"]
        self.active_color = theme_data["color"]["text"]["secondary"]

        # Set icon mặc định
        if self.icon_path.exists():
            self.btn.setIcon(load_svg_colored(self.icon_path, self.normal_color, 20))
            self.btn.setIconSize(QSize(20, 20))

        # Khi toggle (active)
        self.btn.toggled.connect(self._on_toggled)

        # Override hover
        self.btn.enterEvent = self._on_enter
        self.btn.leaveEvent = self._on_leave

    def widget(self):
        return self.btn

    def _on_toggled(self, checked: bool):
        """Đổi màu icon khi active / inactive"""
        if self.icon_path.exists():
            color = self.active_color if checked else self.normal_color
            self.btn.setIcon(load_svg_colored(self.icon_path, color, 20))

    def _on_enter(self, event):
        """Đổi màu icon khi hover"""
        if self.icon_path.exists() and not self.btn.isChecked():
            self.btn.setIcon(load_svg_colored(self.icon_path, self.hover_color, 20))
        QPushButton.enterEvent(self.btn, event)

    def _on_leave(self, event):
        """Trả lại màu icon khi rời hover"""
        if self.icon_path.exists() and not self.btn.isChecked():
            self.btn.setIcon(load_svg_colored(self.icon_path, self.normal_color, 20))
        QPushButton.leaveEvent(self.btn, event)


# ============================================================
#                     SidePanel
# ============================================================
class SidePanel(QWidget):
    page_selected = Signal(str)

    def __init__(self, project_root: Path, theme_manager: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SidePanel")

        self.theme_manager = theme_manager
        theme_data = theme_manager.get_theme_data()
        self.version = theme_data["theme"]["version"]

        # Layout chính
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # --- Logo ---
        logo_path = resource_path("assets/logo/logo-text.png")
        logo_label = QLabel()
        logo_pixmap = QPixmap(str(logo_path))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaledToWidth(100, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(logo_label)

        layout.addItem(QSpacerItem(0, 60, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Navigation buttons ---
        self.buttons: dict[str, NavButton] = {}
        pages = [
            ("home", "Home", "home.svg"),
            ("extra_info", "Extract Info", "scan.svg"),
            ("file_log", "File Log", "folder.svg"),
            ("setting", "Setting", "setting.svg"),
            ("review", "Review", "review.svg"),
        ]

        for key, text, icon_file in pages:
            icon_path = resource_path(f"assets/icon/{icon_file}")
            nav_btn = NavButton(key, text, icon_path, theme_data)
            nav_btn.btn.clicked.connect(lambda checked, k=key: self.page_selected.emit(k))

            layout.addWidget(nav_btn.widget())
            self.buttons[key] = nav_btn

        layout.addStretch(1)

        # --- User info at bottom ---
        user_icon_path = resource_path("assets/icon/user.svg")
        user_icon_label = QLabel()
        if user_icon_path.exists():
            user_icon_label.setPixmap(
                load_svg_colored(user_icon_path, theme_data["color"]["text"]["primary"], 24).pixmap(24, 24)
            )
        user_icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(user_icon_label)

        user_label = QLabel("User/Administrator")
        user_label.setObjectName("UserLabel")
        user_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(user_label)

        version_label = QLabel(f"Version {self.version}")
        version_label.setObjectName("VersionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Default active
        if "home" in self.buttons:
            self.buttons["home"].btn.setChecked(True)

    def set_active(self, key: str) -> None:
        """Đặt trạng thái active cho button theo key"""
        if key in self.buttons:
            self.buttons[key].btn.setChecked(True)
