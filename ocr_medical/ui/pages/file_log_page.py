from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager

class FileLogPage(BasePage):
    """
    Trang hiển thị lịch sử các file đã xử lý.
    TODO: Thêm table/list view để hiển thị file log.
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("File Log", theme_manager, parent)
        layout = self.layout()

        # TODO: Thêm widget hiển thị danh sách file log
        
        layout.addStretch(1)