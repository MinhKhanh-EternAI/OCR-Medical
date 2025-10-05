from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager

class ReviewPage(BasePage):
    """
    Trang review kết quả sau khi xử lý OCR.
    TODO: Thêm UI để hiển thị và chỉnh sửa kết quả.
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Review", theme_manager, parent)
        
        layout = self.layout()

        # TODO: Thêm widget hiển thị kết quả OCR
        # - Table/Form hiển thị thông tin đã trích xuất
        # - Nút chỉnh sửa
        # - Nút export
        
        # Nằm chân trang
        layout.addStretch(1)