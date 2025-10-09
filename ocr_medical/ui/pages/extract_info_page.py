from __future__ import annotations
from PySide6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                                QProgressBar, QMessageBox, QWidget, QScrollArea, QFrame,
                                QSplitter, QLineEdit, QFileDialog)
from PySide6.QtCore import Qt, QThread, Signal, QMutex, QMutexLocker, QSize
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import Optional
import traceback

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.core.pipeline import process_input
from ocr_medical.core.status import status_manager


class ProcessingFileItem(QFrame):
    """Widget hiển thị 1 file đang xử lý với trạng thái"""
    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.setObjectName("ProcessingFileItem")
        self.file_path = file_path
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        
        self.name_label = QLabel(file_path.name)
        self.name_label.setObjectName("ProcessingFileName")
        layout.addWidget(self.name_label, stretch=1)
        
        self.status_label = QLabel("⏳ Waiting")
        self.status_label.setObjectName("ProcessingFileStatus")
        layout.addWidget(self.status_label)
    
    def set_status(self, status: str):
        status_map = {
            "processing": ("🔄 Processing", "#175CD3"),
            "success": ("✅ Done", "#4CAF50"),
            "error": ("❌ Error", "#F44336"),
            "waiting": ("⏳ Waiting", "#999")
        }
        text, color = status_map.get(status, ("⏳ Waiting", "#999"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")


class ExtraInfoPage(BasePage):
    """
    Trang xử lý OCR và trích xuất thông tin
    Layout: Bên trái (ảnh + file list), Bên phải (thông tin trích xuất)
    """
    log_update = Signal(str)
    progress_update = Signal(int)
    navigate_back_requested = Signal()
    file_status_changed = Signal(Path, str)

    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Extract Info", theme_manager, parent)
        layout = self.layout()
        
        self.thread: Optional[PipelineThread] = None
        self.file_widgets: dict[Path, ProcessingFileItem] = {}

        splitter = QSplitter(Qt.Horizontal)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.image_label = QLabel()
        self.image_label.setObjectName("ProcessedImagePreview")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 300)
        self.image_label.setStyleSheet("border: 1px solid #ddd; background: #f5f5f5;")
        self.image_label.setText("Preview will appear here")
        left_layout.addWidget(self.image_label)
        
        files_label = QLabel("Processing Files:")
        files_label.setObjectName("SectionLabel")
        left_layout.addWidget(files_label)
        
        self.files_scroll = QScrollArea()
        self.files_scroll.setObjectName("ProcessingFilesList")
        self.files_scroll.setWidgetResizable(True)
        self.files_scroll.setMaximumHeight(150)
        
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setContentsMargins(0, 0, 0, 0)
        self.files_layout.setSpacing(2)
        self.files_layout.setAlignment(Qt.AlignTop)
        
        self.files_scroll.setWidget(self.files_container)
        left_layout.addWidget(self.files_scroll)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        info_header = QLabel("Extracted Information:")
        info_header.setObjectName("SectionLabel")
        right_layout.addWidget(info_header)
        
        self.info_text = QTextEdit()
        self.info_text.setObjectName("ExtractedInfoBox")
        self.info_text.setReadOnly(False)
        self.info_text.setPlaceholderText("Extracted information will appear here...")
        right_layout.addWidget(self.info_text)
        
        output_layout = QHBoxLayout()
        output_label = QLabel("Save as:")
        output_layout.addWidget(output_label)
        
        self.output_name = QLineEdit()
        self.output_name.setObjectName("OutputNameEdit")
        self.output_name.setPlaceholderText("result")
        output_layout.addWidget(self.output_name, stretch=1)
        
        self.output_path = QLineEdit()
        self.output_path.setObjectName("OutputPathEdit")
        default_output = Path(__file__).resolve().parent.parent.parent / "data" / "output"
        self.output_path.setText(str(default_output))
        self.output_path.setReadOnly(True)
        output_layout.addWidget(self.output_path, stretch=2)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_output_path)
        output_layout.addWidget(browse_btn)
        
        right_layout.addLayout(output_layout)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self._go_back)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelButton")
        self.cancel_btn.clicked.connect(self._cancel_processing)
        self.cancel_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self._save_changes)
        self.save_btn.setEnabled(False)
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.save_btn)
        layout.addLayout(btn_layout)

        self.log_update.connect(self._append_log)
        self.progress_update.connect(self._set_progress)
        self.file_status_changed.connect(self._update_file_status)

    def load_files(self, files: list[Path]):
        if not files:
            return

        if self.thread is not None and self.thread.isRunning():
            self.thread.cancel()
            self.thread.wait()

        self.info_text.clear()
        self.image_label.clear()
        self.image_label.setText("Processing...")
        self.progress_bar.setValue(0)
        
        while self.files_layout.count():
            item = self.files_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.file_widgets.clear()
        
        for file in files:
            item = ProcessingFileItem(file)
            self.files_layout.addWidget(item)
            self.file_widgets[file] = item
        
        self.cancel_btn.setEnabled(True)
        self.back_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        self.thread = PipelineThread(files)
        self.thread.log_update.connect(self.log_update.emit)
        self.thread.progress_update.connect(self.progress_update.emit)
        self.thread.file_status_changed.connect(self.file_status_changed.emit)
        self.thread.image_processed.connect(self._display_image)
        self.thread.info_extracted.connect(self._display_info)
        self.thread.finished.connect(self._on_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _append_log(self, msg: str):
        pass

    def _set_progress(self, value: int):
        self.progress_bar.setValue(value)

    def _update_file_status(self, file_path: Path, status: str):
        if file_path in self.file_widgets:
            self.file_widgets[file_path].set_status(status)

    def _display_image(self, image_path: Path):
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            scaled = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled)

    def _display_info(self, info: str):
        self.info_text.setPlainText(info)

    def _on_finished(self):
        self.progress_bar.setValue(100)
        self.cancel_btn.setEnabled(False)
        self.back_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def _go_back(self):
        self.navigate_back_requested.emit()
    
    def _cancel_processing(self):
        if self.thread and self.thread.isRunning():
            reply = QMessageBox.question(
                self,
                'Cancel Processing',
                'Are you sure you want to cancel?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.thread.cancel()
                self.cancel_btn.setEnabled(False)
    
    def _browse_output_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select output directory")
        if folder:
            self.output_path.setText(folder)
    
    def _save_changes(self):
        QMessageBox.information(self, "Saved", "Changes saved successfully!")


class PipelineThread(QThread):
    log_update = Signal(str)
    progress_update = Signal(int)
    file_status_changed = Signal(Path, str)
    image_processed = Signal(Path)
    info_extracted = Signal(str)
    finished = Signal()

    def __init__(self, files: list[Path]):
        super().__init__()
        self.files = files
        self._is_cancelled = False
        self._lock = QMutex()

    def cancel(self):
        with QMutexLocker(self._lock):
            self._is_cancelled = True

    def run(self):
        total = len(self.files)
        success_count = 0
        error_count = 0
        
        for i, file in enumerate(self.files, start=1):
            with QMutexLocker(self._lock):
                if self._is_cancelled:
                    self.log_update.emit("⚠️ Processing cancelled by user")
                    self.finished.emit()
                    return
            
            self.file_status_changed.emit(file, "processing")
            self.log_update.emit(f"🔹 [{i}/{total}] Processing: {file.name}")

            try:
                status_manager.reset()
                process_input(str(file))
                
                for log in status_manager.logs:
                    self.log_update.emit(f"   {log}")
                
                processed_path = Path(__file__).resolve().parent.parent.parent / "data" / "output" / file.stem / "processed" / f"{file.stem}_processed.png"
                if processed_path.exists():
                    self.image_processed.emit(processed_path)
                
                text_path = Path(__file__).resolve().parent.parent.parent / "data" / "output" / file.stem / "text" / f"{file.stem}_processed.md"
                if text_path.exists():
                    with open(text_path, 'r', encoding='utf-8') as f:
                        self.info_extracted.emit(f.read())
                
                self.log_update.emit(f"✅ Success: {file.name}")
                self.file_status_changed.emit(file, "success")
                success_count += 1

            except FileNotFoundError:
                self.log_update.emit(f"❌ File not found: {file.name}")
                self.file_status_changed.emit(file, "error")
                error_count += 1
            except PermissionError:
                self.log_update.emit(f"❌ Permission denied: {file.name}")
                self.file_status_changed.emit(file, "error")
                error_count += 1
            except Exception as e:
                self.log_update.emit(f"❌ Error processing {file.name}: {e}")
                self.log_update.emit(f"   Traceback: {traceback.format_exc()}")
                self.file_status_changed.emit(file, "error")
                error_count += 1

            percent = int(i / total * 100)
            self.progress_update.emit(percent)

        self.log_update.emit(f"\n{'='*50}")
        self.log_update.emit(f"✅ Successful: {success_count}/{total}")
        self.log_update.emit(f"❌ Failed: {error_count}/{total}")
        self.log_update.emit(f"{'='*50}")

        self.finished.emit()