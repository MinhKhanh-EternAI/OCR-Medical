from __future__ import annotations
from PySide6.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QPushButton, QProgressBar, QHBoxLayout
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.core.pipeline import process_input
from ocr_medical.core.status import status_manager


class ExtraInfoPage(BasePage):
    """
    Trang xử lý OCR và trích xuất thông tin từ các file đầu vào.
    Hiển thị tiến trình, log và cung cấp nút điều hướng.
    """
    # Signal để cập nhật log và progress bar từ thread
    log_update = Signal(str)
    progress_update = Signal(int)

    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Extract Info", theme_manager, parent)
        layout = self.layout()

        # --- Tiêu đề phụ: hiển thị trạng thái ---
        self.info_label = QLabel("Waiting for input files...")
        self.info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.info_label)

        # --- Thanh tiến trình ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # --- Log box: hiển thị chi tiết quá trình xử lý ---
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)  # Chỉ đọc, không cho chỉnh sửa
        layout.addWidget(self.log_box, stretch=1)

        # --- Nút điều khiển ---
        btn_layout = QHBoxLayout()
        
        # Nút quay lại trang Home
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self._go_back)
        
        # Nút mở thư mục output
        self.save_btn = QPushButton("Open Output Folder")
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addStretch(1)  # Đẩy nút save sang phải
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        # --- Connect signal nội bộ để cập nhật UI từ thread ---
        self.log_update.connect(self._append_log)
        self.progress_update.connect(self._set_progress)

        layout.addStretch(1)

    def load_files(self, files: list[Path]):
        """
        Nhận danh sách file từ HomePage và bắt đầu xử lý pipeline.
        Chạy trong thread riêng để không làm đơ UI.
        """
        if not files:
            self.info_label.setText("⚠️ No files provided.")
            return

        # Reset UI
        self.log_box.clear()
        self.info_label.setText(f"Processing {len(files)} file(s)...")
        self.progress_bar.setValue(0)

        # Tạo và chạy thread pipeline
        self.thread = PipelineThread(files)
        self.thread.log_update.connect(self.log_update.emit)
        self.thread.progress_update.connect(self.progress_update.emit)
        self.thread.finished.connect(self._on_finished)
        self.thread.start()

    def _append_log(self, msg: str):
        """Thêm dòng log vào log box"""
        self.log_box.append(msg)

    def _set_progress(self, value: int):
        """Cập nhật giá trị thanh tiến trình"""
        self.progress_bar.setValue(value)

    def _on_finished(self):
        """Callback khi pipeline hoàn thành"""
        self.info_label.setText("✅ Done! Results saved to data/output/")
        self.progress_bar.setValue(100)

    def _go_back(self):
        """Quay về trang Home"""
        from ui.main_window import MainWindow
        main = self.window()
        if isinstance(main, MainWindow):
            main.navigate_to("home")


class PipelineThread(QThread):
    """
    Thread chạy pipeline OCR để không chặn giao diện.
    Emit signal để cập nhật progress và log.
    """
    log_update = Signal(str)
    progress_update = Signal(int)
    finished = Signal()

    def __init__(self, files: list[Path]):
        super().__init__()
        self.files = files

    def run(self):
        """Xử lý từng file trong danh sách"""
        total = len(self.files)
        
        for i, file in enumerate(self.files, start=1):
            # Log file đang xử lý
            self.log_update.emit(f"🔹 [{i}/{total}] Đang xử lý: {file.name}")

            try:
                # Gọi pipeline thực tế
                status_manager.reset()
                process_input(str(file))
                
                # Emit tất cả log từ status_manager
                for log in status_manager.logs:
                    self.log_update.emit(f"   {log}")

            except Exception as e:
                # Log lỗi nếu có
                self.log_update.emit(f"❌ Lỗi khi xử lý {file.name}: {e}")

            # Cập nhật progress bar
            percent = int(i / total * 100)
            self.progress_update.emit(percent)

        # Báo hiệu hoàn thành
        self.finished.emit()