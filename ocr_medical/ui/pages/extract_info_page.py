from .base_page import BasePage
from ui.style.theme_manager import ThemeManager

class ExtraInfoPage(BasePage):
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Extra Info", theme_manager, parent)
