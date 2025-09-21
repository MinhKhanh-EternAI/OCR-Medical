from PySide6.QtWidgets import QVBoxLayout, QLabel, QComboBox
from .base_page import BasePage
from ui.style.theme_manager import ThemeManager


class SettingPage(BasePage):
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Settings", theme_manager, parent)

        # --- Thêm combobox đổi theme ---
        layout: QVBoxLayout = self.layout()
        label = QLabel("Theme:")
        layout.addWidget(label)

        combo = QComboBox()
        combo.addItems(["light", "dark"])
        combo.setCurrentText(theme_manager.get_theme_name())
        combo.currentTextChanged.connect(theme_manager.set_theme)
        layout.addWidget(combo)
