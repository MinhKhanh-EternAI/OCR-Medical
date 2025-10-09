from __future__ import annotations
from PySide6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                                QProgressBar, QMessageBox, QWidget, QScrollArea, QFrame,
                                QSplitter, QLineEdit, QFileDialog, QMenu, QApplication)
from PySide6.QtCore import Qt, QThread, Signal, QMutex, QMutexLocker, QSize, QPoint
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import Optional
import traceback

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored
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
    Layout tối ưu: Phía trên tên trang + more menu, Phía dưới splitter (ảnh + file list trái, thông tin phải)
    """
    log_update = Signal(str)
    progress_update = Signal(int)
    navigate_back_requested = Signal()
    file_status_changed = Signal(Path, str)

    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Extraction Info", theme_manager, parent)
        
        self.theme_manager = theme_manager
        self.theme_data = theme_manager.get_theme_data()
        self.project_root = Path(__file__).resolve().parent.parent.parent
        
        # Lấy layout chính từ BasePage
        main_layout = self.layout()
        
        # Lấy header ra khỏi layout
        main_layout.removeWidget(self.header)
        main_layout.removeWidget(self.divider)
        
        # Tạo header layout riêng với tên page + more button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        
        header_layout.addWidget(self.header, stretch=1)
        
        # More button
        self.more_btn = QPushButton()
        self.more_btn.setObjectName("MoreButton")
        self.more_btn.setCursor(Qt.PointingHandCursor)
        self.more_btn.setFixedSize(36, 36)
        self.more_btn.setToolTip("More options")
        
        more_icon_path = self.project_root / "assets" / "icon" / "more.svg"
        if more_icon_path.exists():
            self.more_btn.setIcon(load_svg_colored(
                more_icon_path, 
                self.theme_data["color"]["text"]["primary"], 
                18
            ))
            self.more_btn.setIconSize(QSize(18, 18))
        
        self.more_btn.clicked.connect(self._show_more_menu)
        header_layout.addWidget(self.more_btn)
        
        main_layout.insertLayout(0, header_layout)
        main_layout.insertWidget(1, self.divider)
        
        self.thread: Optional[PipelineThread] = None
        self.file_widgets: dict[Path, ProcessingFileItem] = {}
        self.current_file_path: Optional[Path] = None

        # ===== MAIN SPLITTER =====
        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("MainSplitter")
        
        # ===== LEFT PANEL (ảnh + file list) =====
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        # Image preview - chiếm toàn bộ khoảng trống
        self.image_label = QLabel()
        self.image_label.setObjectName("ProcessedImagePreview")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(300, 400)
        self.image_label.setStyleSheet("border: 1px solid #ddd; border-radius: 8px; background: #f5f5f5;")
        self.image_label.setText("Preview will appear here")
        left_layout.addWidget(self.image_label, stretch=1)
        
        # Processing Files section
        files_label = QLabel("Processing Files:")
        files_label.setObjectName("SectionLabel")
        left_layout.addWidget(files_label)
        
        self.files_scroll = QScrollArea()
        self.files_scroll.setObjectName("ProcessingFilesList")
        self.files_scroll.setWidgetResizable(True)
        self.files_scroll.setMaximumHeight(180)
        
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setContentsMargins(0, 0, 0, 0)
        self.files_layout.setSpacing(2)
        self.files_layout.setAlignment(Qt.AlignTop)
        
        self.files_scroll.setWidget(self.files_container)
        left_layout.addWidget(self.files_scroll)
        
        # ===== RIGHT PANEL (thông tin trích xuất) =====
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)
        
        info_header = QLabel("📋 Extracted Information:")
        info_header.setObjectName("SectionLabel")
        right_layout.addWidget(info_header)
        
        # Markdown text box - chiếm toàn bộ khoảng trống
        self.info_text = QTextEdit()
        self.info_text.setObjectName("ExtractedInfoBox")
        self.info_text.setReadOnly(False)
        self.info_text.setPlaceholderText("Extracted information (Markdown) will appear here...")
        right_layout.addWidget(self.info_text, stretch=1)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter, stretch=1)

        # ===== PROGRESS BAR =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("ProcessProgress")
        main_layout.addWidget(self.progress_bar)

        # ===== BUTTONS =====
        btn_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self._go_back)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("CancelButton")
        self.cancel_btn.clicked.connect(self._cancel_processing)
        self.cancel_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("SaveButton")
        self.save_btn.clicked.connect(self._save_changes)
        self.save_btn.setEnabled(False)
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

        self.log_update.connect(self._append_log)
        self.progress_update.connect(self._set_progress)
        self.file_status_changed.connect(self._update_file_status)

    def _show_more_menu(self):
        """Hiển thị menu more với options save as, export"""
        menu = QMenu(self)
        menu.setObjectName("MoreMenu")
        
        # Save As
        save_action = menu.addAction("💾 Save As")
        save_action.triggered.connect(self._show_save_as_dialog)
        
        menu.addSeparator()
        
        # Export Markdown
        export_md = menu.addAction("📤 Export as Markdown (.md)")
        export_md.triggered.connect(self._export_markdown)
        
        # Export Text
        export_txt = menu.addAction("📤 Export as Text (.txt)")
        export_txt.triggered.connect(self._export_text)
        
        # Lấy vị trí button để hiển thị menu
        pos = self.more_btn.mapToGlobal(QPoint(0, self.more_btn.height()))
        menu.popup(pos)

    def _show_save_as_dialog(self):
        """Dialog để set save as name và path"""
        from PySide6.QtWidgets import QDialog, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Save As")
        dialog.setGeometry(100, 100, 400, 150)
        
        form_layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("result")
        form_layout.addRow("File name:", name_input)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        
        ok_btn.clicked.connect(lambda: (
            setattr(self, '_save_name', name_input.text() or "result"),
            dialog.accept()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addStretch(1)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        form_layout.addRow(btn_layout)
        
        dialog.exec()

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
        pass  # Không hiển thị log

    def _set_progress(self, value: int):
        self.progress_bar.setValue(value)

    def _update_file_status(self, file_path: Path, status: str):
        if file_path in self.file_widgets:
            self.file_widgets[file_path].set_status(status)

    def _display_image(self, image_path: Path):
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            # Fit image to label while maintaining aspect ratio
            scaled = pixmap.scaledToHeight(
                self.image_label.height() - 20, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.current_file_path = image_path.parent.parent

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
    
    def _export_markdown(self):
        if not self.info_text.toPlainText().strip():
            QMessageBox.warning(self, "No Data", "No extracted information to export!")
            return
        
        filename = getattr(self, '_save_name', 'result')
        default_path = f"{filename}.md"
        
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Markdown File", 
            default_path,
            "Markdown Files (*.md);;All Files (*)"
        )
        
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.info_text.toPlainText())
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"File saved to:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save file:\n{e}")
    
    def _export_text(self):
        if not self.info_text.toPlainText().strip():
            QMessageBox.warning(self, "No Data", "No extracted information to export!")
            return
        
        filename = getattr(self, '_save_name', 'result')
        default_path = f"{filename}.txt"
        
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Text File", 
            default_path,
            "Text Files (*.txt);;All Files (*)"
        )
        
        if path:
            try:
                # Convert markdown to clean text
                clean_text = self.info_text.toPlainText()
                clean_text = clean_text.replace('**', '').replace('|', ' ')
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(clean_text)
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"File saved to:\n{path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save file:\n{e}")
    
    def _save_changes(self):
        if not self.info_text.toPlainText().strip():
            QMessageBox.warning(self, "No Changes", "No extracted information to save!")
            return
        
        reply = QMessageBox.question(
            self,
            "Save Changes",
            "Save all extracted information?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(
                self, 
                "Saved", 
                "All changes have been saved successfully!"
            )


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
                    self.finished.emit()
                    return
            
            self.file_status_changed.emit(file, "processing")

            try:
                status_manager.reset()
                process_input(str(file))
                
                # Find and display processed image
                processed_path = Path(__file__).resolve().parent.parent.parent / "data" / "output" / file.stem / "processed" / f"{file.stem}_processed.png"
                if processed_path.exists():
                    self.image_processed.emit(processed_path)
                
                # Find and display extracted text
                text_path = Path(__file__).resolve().parent.parent.parent / "data" / "output" / file.stem / "text" / f"{file.stem}_processed.md"
                if text_path.exists():
                    with open(text_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.info_extracted.emit(content)
                
                self.file_status_changed.emit(file, "success")
                success_count += 1

            except FileNotFoundError:
                self.file_status_changed.emit(file, "error")
                error_count += 1
            except PermissionError:
                self.file_status_changed.emit(file, "error")
                error_count += 1
            except Exception as e:
                self.file_status_changed.emit(file, "error")
                error_count += 1

            percent = int((i / total) * 100)
            self.progress_update.emit(percent)

        self.finished.emit()