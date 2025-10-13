from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt
from typing import Optional


class DialogManager:
    """
    Manager for all application dialogs
    Tập trung quản lý tất cả QMessageBox để dễ chỉnh sửa giao diện
    """

    # Dialog style settings
    BUTTON_WIDTH = 80
    DIALOG_WIDTH = 400
    DIALOG_HEIGHT = 200

    @staticmethod
    def information(
        parent,
        title: str,
        message: str,
        detail: Optional[str] = None
    ) -> int:
        """
        Hiển thị dialog Information
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main message
            detail: Detailed message (optional)
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        if detail:
            msg_box.setDetailedText(detail)
        
        DialogManager._apply_style(msg_box)
        return msg_box.exec()

    @staticmethod
    def warning(
        parent,
        title: str,
        message: str,
        detail: Optional[str] = None
    ) -> int:
        """
        Hiển thị dialog Warning
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main message
            detail: Detailed message (optional)
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        if detail:
            msg_box.setDetailedText(detail)
        
        DialogManager._apply_style(msg_box)
        return msg_box.exec()

    @staticmethod
    def critical(
        parent,
        title: str,
        message: str,
        detail: Optional[str] = None
    ) -> int:
        """
        Hiển thị dialog Critical/Error
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main message
            detail: Detailed message (optional)
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        if detail:
            msg_box.setDetailedText(detail)
        
        DialogManager._apply_style(msg_box)
        return msg_box.exec()

    @staticmethod
    def question(
        parent,
        title: str,
        message: str,
        buttons: int = QMessageBox.Yes | QMessageBox.No,
        default_button: int = QMessageBox.No,
        detail: Optional[str] = None
    ) -> int:
        """
        Hiển thị dialog Question với các nút tùy chọn
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Main message
            buttons: Button combination (QMessageBox.Yes | QMessageBox.No, etc.)
            default_button: Default button to focus
            detail: Detailed message (optional)
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setStandardButtons(buttons)
        msg_box.setDefaultButton(default_button)
        
        if detail:
            msg_box.setDetailedText(detail)
        
        DialogManager._apply_style(msg_box)
        return msg_box.exec()

    @staticmethod
    def confirm_delete(
        parent,
        item_name: str
    ) -> int:
        """
        Hiển thị dialog confirm delete
        
        Args:
            parent: Parent widget
            item_name: Name of item to delete
        """
        return DialogManager.question(
            parent,
            "Confirm Delete",
            f'Remove "{item_name}" from the list?',
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.No
        )

    @staticmethod
    def confirm_process(
        parent,
        file_count: int
    ) -> int:
        """
        Hiển thị dialog confirm process files
        
        Args:
            parent: Parent widget
            file_count: Number of files to process
        """
        return DialogManager.question(
            parent,
            "Process Files",
            f"Start processing {file_count} file(s)?",
            buttons=QMessageBox.Yes | QMessageBox.No,
            default_button=QMessageBox.Yes
        )

    @staticmethod
    def _apply_style(msg_box: QMessageBox):
        """
        Áp dụng style chung cho tất cả dialogs
        Thay đổi ở đây sẽ ảnh hưởng tới tất cả dialogs
        """
        # Disable focus policy cho tất cả buttons
        for button in msg_box.buttons():
            button.setFocusPolicy(Qt.NoFocus)
        
        # Thiết lập kích thước dialog
        msg_box.setMinimumWidth(DialogManager.DIALOG_WIDTH)
        
        # Optional: Set stylesheet nếu cần
        # msg_box.setStyleSheet("""
        #     QMessageBox {
        #         background-color: #f5f5f5;
        #     }
        #     QMessageBox QLabel {
        #         color: #333333;
        #     }
        # """)