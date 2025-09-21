from .base_page import BasePage
from ui.style.theme_manager import ThemeManager

class HomePage(BasePage):
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("OCR - Medical", theme_manager, parent)
