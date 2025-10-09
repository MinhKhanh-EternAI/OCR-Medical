from __future__ import annotations
from PySide6.QtWidgets import (QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                                QProgressBar, QMessageBox, QWidget, QScrollArea, QFrame,
                                QSplitter, QFileDialog, QMenu, QTabWidget, QGraphicsView,
                                QGraphicsScene, QGraphicsPixmapItem)
from PySide6.QtCore import Qt, QThread, Signal, QMutex, QMutexLocker, QSize, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen
from pathlib import Path
from typing import Optional
import markdown

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored
from ocr_medical.core.pipeline import process_input
from ocr_medical.core.status import status_manager


class ImageViewer(QGraphicsView):
    """Viewer hiển thị ảnh với zoom và pan"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ImageViewer")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setBackgroundBrush(QColor("#2a2a2a"))
        
        self.pixmap_item: Optional[QGraphicsPixmapItem] = None
        self.zoom_factor = 1.0
        
    def set_image(self, pixmap: QPixmap):
        """Set ảnh mới"""
        self.scene.clear()
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.zoom_factor = 1.0
        self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        
    def wheelEvent(self, event):
        """Zoom bằng scroll wheel"""
        if self.pixmap_item:
            zoom_in = event.angleDelta().y() > 0
            zoom_amount = 1.15 if zoom_in else 1 / 1.15
            self.zoom_factor *= zoom_amount
            self.scale(zoom_amount, zoom_amount)
    
    def reset_zoom(self):
        """Reset về fit view"""
        if self.pixmap_item:
            self.resetTransform()
            self.zoom_factor = 1.0
            self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)


class ProcessingFileItem(QFrame):
    """Widget hiển thị 1 file đang xử lý với trạng thái"""
    def __init__(self, file_path: Path, parent=None):
        super().__init__(parent)
        self.setObjectName("ProcessingFileItem")
        self.file_path = file_path
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        self.name_label = QLabel(file_path.name)
        self.name_label.setObjectName("ProcessingFileName")
        layout.addWidget(self.name_label, stretch=1)
        
        self.status_label = QLabel("⏳ Waiting")
        self.status_label.setObjectName("ProcessingFileStatus")
        layout.addWidget(self.status_label)
        
        # Animation cho loading
        self.loading_dots = 0
        self.loading_timer = None
    
    def set_status(self, status: str):
        status_map = {
            "processing": ("🔄 Processing", "#175CD3"),
            "success": ("✅ Done", "#4CAF50"),
            "error": ("❌ Error", "#F44336"),
            "waiting": ("⏳ Waiting", "#999")
        }
        text, color = status_map.get(status, ("⏳ Waiting", "#999"))
        
        if status == "processing":
            self._start_loading_animation()
        else:
            self._stop_loading_animation()
            
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: 600;")
    
    def _start_loading_animation(self):
        """Bắt đầu hiệu ứng loading dots"""
        from PySide6.QtCore import QTimer
        if not self.loading_timer:
            self.loading_timer = QTimer(self)
            self.loading_timer.timeout.connect(self._update_loading_dots)
            self.loading_timer.start(400)
    
    def _stop_loading_animation(self):
        """Dừng hiệu ứng loading"""
        if self.loading_timer:
            self.loading_timer.stop()
            self.loading_timer = None
    
    def _update_loading_dots(self):
        """Cập nhật dots animation"""
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = "." * self.loading_dots
        self.status_label.setText(f"🔄 Processing{dots}")


class ExtraInfoPage(BasePage):
    """Trang xử lý OCR và trích xuất thông tin"""
    log_update = Signal(str)
    progress_update = Signal(int)
    navigate_back_requested = Signal()
    file_status_changed = Signal(Path, str)

    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Extraction Info", theme_manager, parent)
        
        self.theme_manager = theme_manager
        self.theme_data = theme_manager.get_theme_data()
        self.project_root = Path(__file__).resolve().parent.parent.parent
        
        main_layout = self.layout()
        
        # === HEADER với More Button ===
        main_layout.removeWidget(self.header)
        main_layout.removeWidget(self.divider)
        
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
        self.current_markdown: str = ""

        # === MAIN SPLITTER (3:7 ratio) ===
        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("MainSplitter")
        splitter.setHandleWidth(0)  # Không cho kéo
        
        # === LEFT PANEL (File Preview) ===
        left_panel = QWidget()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        # Header với fullscreen button
        preview_header = QHBoxLayout()
        preview_label = QLabel("📸 File Preview")
        preview_label.setObjectName("SectionLabel")
        preview_header.addWidget(preview_label)
        preview_header.addStretch(1)
        
        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setObjectName("IconButton")
        self.fullscreen_btn.setFixedSize(32, 32)
        self.fullscreen_btn.setCursor(Qt.PointingHandCursor)
        self.fullscreen_btn.setToolTip("Fullscreen")
        
        fullscreen_icon = self.project_root / "assets" / "icon" / "full_screen.svg"
        if fullscreen_icon.exists():
            self.fullscreen_btn.setIcon(load_svg_colored(
                fullscreen_icon, 
                self.theme_data["color"]["text"]["primary"], 
                18
            ))
        self.fullscreen_btn.clicked.connect(self._toggle_fullscreen)
        preview_header.addWidget(self.fullscreen_btn)
        
        left_layout.addLayout(preview_header)
        
        # Image viewer
        self.image_viewer = ImageViewer()
        self.image_viewer.setMinimumSize(300, 400)
        left_layout.addWidget(self.image_viewer, stretch=1)
        
        # Processing Files List
        files_label = QLabel("🗂️ Processing Files:")
        files_label.setObjectName("SectionLabel")
        left_layout.addWidget(files_label)
        
        self.files_scroll = QScrollArea()
        self.files_scroll.setObjectName("ProcessingFilesList")
        self.files_scroll.setWidgetResizable(True)
        self.files_scroll.setMaximumHeight(160)
        
        self.files_container = QWidget()
        self.files_layout = QVBoxLayout(self.files_container)
        self.files_layout.setContentsMargins(0, 0, 0, 0)
        self.files_layout.setSpacing(4)
        self.files_layout.setAlignment(Qt.AlignTop)
        
        self.files_scroll.setWidget(self.files_container)
        left_layout.addWidget(self.files_scroll)
        
        # === RIGHT PANEL (Result Display) ===
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)
        
        info_header = QLabel("📋 Result Display")
        info_header.setObjectName("SectionLabel")
        right_layout.addWidget(info_header)
        
        # Tab widget cho Preview và Raw
        self.result_tabs = QTabWidget()
        self.result_tabs.setObjectName("ResultTabs")
        
        # Preview tab (HTML render)
        self.preview_text = QTextEdit()
        self.preview_text.setObjectName("MarkdownPreview")
        self.preview_text.setReadOnly(True)
        self.result_tabs.addTab(self.preview_text, "📄 Preview")
        
        # Raw tab (markdown source)
        self.raw_text = QTextEdit()
        self.raw_text.setObjectName("MarkdownRaw")
        self.raw_text.setReadOnly(False)
        self.raw_text.setPlaceholderText("Extracted markdown will appear here...")
        self.result_tabs.addTab(self.raw_text, "📝 Raw Markdown")
        
        right_layout.addWidget(self.result_tabs, stretch=1)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter, stretch=1)

        # === STATUS BAR ===
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusLabel")
        main_layout.addWidget(self.status_label)

        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setObjectName("ProcessProgress")
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)

        # === BUTTONS ===
        btn_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("  Back")
        self.back_btn.setObjectName("BackButton")
        back_icon = self.project_root / "assets" / "icon" / "back_page.svg"
        if back_icon.exists():
            self.back_btn.setIcon(load_svg_colored(
                back_icon,
                self.theme_data["color"]["text"]["primary"],
                18
            ))
        self.back_btn.clicked.connect(self._go_back)
        
        self.cancel_btn = QPushButton("  Stop OCR")
        self.cancel_btn.setObjectName("CancelButton")
        stop_icon = self.project_root / "assets" / "icon" / "stop_ocr.svg"
        if stop_icon.exists():
            self.cancel_btn.setIcon(load_svg_colored(
                stop_icon,
                "#ffffff",
                18
            ))
        self.cancel_btn.clicked.connect(self._cancel_processing)
        self.cancel_btn.setEnabled(False)
        
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.setObjectName("SaveButton")
        self.save_btn.clicked.connect(self._save_changes)
        self.save_btn.setEnabled(False)
        
        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

        # Connect signals
        self.log_update.connect(self._append_log)
        self.progress_update.connect(self._set_progress)
        self.file_status_changed.connect(self._update_file_status)
        self.raw_text.textChanged.connect(self._on_markdown_edited)

    def _show_more_menu(self):
        """Hiển thị menu more"""
        menu = QMenu(self)
        menu.setObjectName("MoreMenu")
        
        save_action = menu.addAction("💾 Save As")
        save_action.triggered.connect(self._show_save_as_dialog)
        
        menu.addSeparator()
        
        export_md = menu.addAction("📤 Export as Markdown (.md)")
        export_md.triggered.connect(self._export_markdown)
        
        export_txt = menu.addAction("📤 Export as Text (.txt)")
        export_txt.triggered.connect(self._export_text)
        
        # Căn trái như button more
        pos = self.more_btn.mapToGlobal(QPoint(0, self.more_btn.height()))
        menu.popup(pos)

    def _show_save_as_dialog(self):
        """Dialog save as"""
        from PySide6.QtWidgets import QDialog, QFormLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Save As")
        dialog.setFixedSize(400, 120)
        
        form_layout = QFormLayout(dialog)
        
        from PySide6.QtWidgets import QLineEdit
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

    def _toggle_fullscreen(self):
        """Toggle fullscreen cho image viewer"""
        # Implement fullscreen dialog nếu cần
        pass

    def _on_markdown_edited(self):
        """Khi user edit raw markdown"""
        md_text = self.raw_text.toPlainText()
        self.current_markdown = md_text
        # Update preview
        html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
        self.preview_text.setHtml(html)

    def load_files(self, files: list[Path]):
        if not files:
            return

        if self.thread is not None and self.thread.isRunning():
            self.thread.cancel()
            self.thread.wait()

        self.raw_text.clear()
        self.preview_text.clear()
        self.image_viewer.scene.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")
        
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
        self.thread.status_changed.connect(self._update_status)
        self.thread.image_processed.connect(self._display_image)
        self.thread.info_extracted.connect(self._display_info)
        self.thread.finished.connect(self._on_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def _append_log(self, msg: str):
        pass

    def _set_progress(self, value: int):
        self.progress_bar.setValue(value)

    def _update_status(self, status: str):
        """Cập nhật status hiện tại"""
        self.status_label.setText(status)

    def _update_file_status(self, file_path: Path, status: str):
        if file_path in self.file_widgets:
            self.file_widgets[file_path].set_status(status)

    def _display_image(self, image_path: Path):
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            self.image_viewer.set_image(pixmap)
            self.current_file_path = image_path.parent.parent

    def _display_info(self, info: str):
        self.current_markdown = info
        self.raw_text.setPlainText(info)
        # Auto update preview
        html = markdown.markdown(info, extensions=['tables', 'fenced_code'])
        self.preview_text.setHtml(html)

    def _on_finished(self):
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ All files processed successfully")
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
                self.status_label.setText("⚠️ Processing cancelled by user")
    
    def _export_markdown(self):
        if not self.raw_text.toPlainText().strip():
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
                    f.write(self.raw_text.toPlainText())
                QMessageBox.information(self, "Export Successful", f"File saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save file:\n{e}")
    
    def _export_text(self):
        if not self.raw_text.toPlainText().strip():
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
                clean_text = self.raw_text.toPlainText()
                clean_text = clean_text.replace('**', '').replace('|', ' ')
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(clean_text)
                QMessageBox.information(self, "Export Successful", f"File saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save file:\n{e}")
    
    def _save_changes(self):
        if not self.raw_text.toPlainText().strip():
            QMessageBox.warning(self, "No Changes", "No extracted information to save!")
            return
        
        if self.current_file_path:
            text_path = self.current_file_path / "text" / f"{self.current_file_path.name}_processed.md"
            try:
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(self.raw_text.toPlainText())
                QMessageBox.information(self, "Saved", "Changes saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save:\n{e}")


class PipelineThread(QThread):
    log_update = Signal(str)
    progress_update = Signal(int)
    file_status_changed = Signal(Path, str)
    status_changed = Signal(str)
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
        
        for i, file in enumerate(self.files, start=1):
            with QMutexLocker(self._lock):
                if self._is_cancelled:
                    self.finished.emit()
                    return
            
            self.file_status_changed.emit(file, "processing")
            self.status_changed.emit(f"Processing {file.name} ({i}/{total})")

            try:
                status_manager.reset()
                
                # Simulate processing stages
                self.status_changed.emit(f"🔄 Loading image: {file.name}")
                self.msleep(300)
                
                self.status_changed.emit(f"🖼️ Enhancing image quality...")
                process_input(str(file))
                self.msleep(500)
                
                # Find and display processed image
                processed_path = Path(__file__).resolve().parent.parent.parent / "data" / "output" / file.stem / "processed" / f"{file.stem}_processed.png"
                if processed_path.exists():
                    self.status_changed.emit(f"✅ Image processed: {file.name}")
                    self.image_processed.emit(processed_path)
                
                # OCR stage
                self.status_changed.emit(f"🔍 Extracting text with OCR...")
                self.msleep(500)
                
                # Find and display extracted text
                text_path = Path(__file__).resolve().parent.parent.parent / "data" / "output" / file.stem / "text" / f"{file.stem}_processed.md"
                if text_path.exists():
                    with open(text_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.info_extracted.emit(content)
                    self.status_changed.emit(f"✅ OCR completed: {file.name}")
                
                self.file_status_changed.emit(file, "success")

            except Exception as e:
                self.status_changed.emit(f"❌ Error processing {file.name}: {str(e)}")
                self.file_status_changed.emit(file, "error")

            percent = int((i / total) * 100)
            self.progress_update.emit(percent)

        self.finished.emit()