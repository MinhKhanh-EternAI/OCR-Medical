from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QStackedWidget, QScrollArea, QWidget, QTextBrowser, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QSize, QThread
from PySide6.QtGui import QPixmap, QMovie
from pathlib import Path
import logging
import markdown  # ✅ Thêm để render Markdown thành HTML

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored
from ocr_medical.core.pipeline import process_input

logger = logging.getLogger(__name__)


# =====================================================
#             OCR Worker Thread
# =====================================================
class OCRWorker(QThread):
    """Worker thread để xử lý OCR không block UI"""

    progress = Signal(int, str)  # (index, status)
    result = Signal(int, str, str)  # (index, markdown_text, image_path)
    finished = Signal()
    error = Signal(int, str)  # (index, error_message)

    def __init__(self, files: list[Path], output_root: Path):
        super().__init__()
        self.files = files
        self.output_root = output_root
        self._is_running = True

    def run(self):
        """Xử lý từng file"""
        for idx, file_path in enumerate(self.files):
            if not self._is_running:
                break

            try:
                # Update status: processing
                self.progress.emit(idx, "processing")

                # Process với pipeline
                logger.info(f"Processing file {idx + 1}/{len(self.files)}: {file_path.name}")
                process_input(str(file_path), str(self.output_root))

                # Đọc kết quả markdown
                img_name = file_path.stem
                md_path = self.output_root / img_name / "text" / f"{img_name}_processed.md"
                processed_img = self.output_root / img_name / "processed" / f"{img_name}_processed.png"

                markdown_text = ""
                if md_path.exists():
                    markdown_text = md_path.read_text(encoding="utf-8")

                # Emit result
                self.result.emit(idx, markdown_text, str(processed_img))
                self.progress.emit(idx, "completed")

            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
                self.error.emit(idx, str(e))
                self.progress.emit(idx, "failed")

        self.finished.emit()

    def stop(self):
        """Dừng worker"""
        self._is_running = False


# =====================================================
#             File Row Item (with status update)
# =====================================================
class FileRowItem(QFrame):
    """Một hàng trong danh sách file: index, file name, status"""

    def __init__(self, index: int, file_name: str, state: str, project_root: Path):
        super().__init__()
        self.setObjectName("FileRowItem")
        self.project_root = project_root
        self.current_state = state

        self.layout_main = QHBoxLayout(self)
        self.layout_main.setContentsMargins(12, 6, 12, 6)
        self.layout_main.setSpacing(0)

        # ----- Column 1: Index -----
        self.index_lbl = QLabel(str(index))
        self.index_lbl.setObjectName("FileIndex")
        self.index_lbl.setAlignment(Qt.AlignCenter)
        self.layout_main.addWidget(self.index_lbl, 1)

        # ----- Column 2: File Name -----
        self.name_lbl = QLabel(file_name)
        self.name_lbl.setObjectName("FileName")
        self.layout_main.addWidget(self.name_lbl, 5)

        # ----- Column 3: Status -----
        self.status_container = QWidget()
        self.status_layout = QHBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        self.status_layout.setSpacing(4)
        self.layout_main.addWidget(self.status_container, 3)

        self.update_status(state)

    def update_status(self, state: str):
        """Cập nhật trạng thái hiển thị"""
        self.current_state = state

        # Clear old widgets
        while self.status_layout.count():
            item = self.status_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create new status display
        color_map = {
            "waiting": ("#A0A0A0", "Waiting"),
            "processing": ("#FB923C", "Processing"),
            "completed": ("#22C55E", "Completed"),
            "failed": ("#EF4444", "Failed"),
        }
        color, text = color_map.get(state, ("#A0A0A0", "Waiting"))

        icon_path = self.project_root / "assets" / "icon" / "circle.svg"
        icon = load_svg_colored(icon_path, color, 10)

        icon_lbl = QLabel()
        icon_lbl.setPixmap(icon.pixmap(10, 10))
        icon_lbl.setFixedWidth(14)

        text_lbl = QLabel(text)
        text_lbl.setStyleSheet(f"color: {color}; font-weight: 500;")

        self.status_layout.addWidget(icon_lbl)
        self.status_layout.addWidget(text_lbl)
        self.status_layout.addStretch()


# =====================================================
#                 Extract Info Page
# =====================================================
class ExtraInfoPage(BasePage):
    navigate_back_requested = Signal()

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__("Extraction Info", theme_manager, parent)

        self.theme_manager = theme_manager
        self.theme_data = theme_manager.get_theme_data()
        self.project_root = Path(__file__).resolve().parent.parent.parent

        self.files = []
        self.file_items = []
        self.worker = None
        self.current_preview_index = 0

        layout = self.layout()
        layout.setSpacing(6)

        # =====================================================
        #                     HEADER
        # =====================================================
        layout.removeWidget(self.header)
        layout.removeWidget(self.divider)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        header_layout.addWidget(self.header, stretch=1)

        layout.insertLayout(0, header_layout)
        layout.insertWidget(1, self.divider)

        # =====================================================
        #                     BODY
        # =====================================================
        body_container = QFrame()
        body_container.setObjectName("BodyContainer")
        body_layout = QHBoxLayout(body_container)
        body_layout.setSpacing(12)
        body_layout.setContentsMargins(4, 6, 4, 0)

        # ---------------- LEFT PANEL ----------------
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        title_left = QLabel("File Preview")
        title_left.setObjectName("SectionLabel")
        left_layout.addWidget(title_left)

        self.preview_box = QLabel()
        self.preview_box.setObjectName("PreviewBox")
        self.preview_box.setAlignment(Qt.AlignCenter)
        self.preview_box.setScaledContents(False)
        self.preview_box.setMinimumSize(300, 200)
        self.preview_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        no_img_path = self.project_root / "assets" / "icon" / "no_image.svg"
        if no_img_path.exists():
            icon = load_svg_colored(no_img_path, self.theme_data["color"]["text"]["muted"], 100)
            self.preview_box.setPixmap(icon.pixmap(QSize(100, 100)))
        left_layout.addWidget(self.preview_box, 4)

        # ---------- FILE LIST ----------
        file_list_frame = QFrame()
        file_list_frame.setObjectName("FileListFrame")
        file_list_layout = QVBoxLayout(file_list_frame)
        file_list_layout.setContentsMargins(0, 0, 0, 0)
        file_list_layout.setSpacing(0)

        # Header
        header_row = QFrame()
        header_row.setObjectName("FileListHeader")
        h_layout = QHBoxLayout(header_row)
        h_layout.setContentsMargins(12, 6, 12, 6)
        h_layout.setSpacing(0)

        col1 = QLabel("#")
        col1.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(col1, 1)

        col2 = QLabel("File Name")
        col2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        h_layout.addWidget(col2, 5)

        col3 = QLabel("Status")
        col3.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        h_layout.addWidget(col3, 3)

        file_list_layout.addWidget(header_row)

        # Scroll chứa các dòng
        self.file_scroll = QScrollArea()
        self.file_scroll.setObjectName("FileScroll")
        self.file_scroll.setWidgetResizable(True)

        self.file_container = QWidget()
        self.file_container.setObjectName("FileListContainer")

        self.file_container_layout = QVBoxLayout(self.file_container)
        self.file_container_layout.setContentsMargins(0, 0, 0, 0)
        self.file_container_layout.setSpacing(0)
        self.file_container_layout.setAlignment(Qt.AlignTop)

        self.file_scroll.setWidget(self.file_container)
        file_list_layout.addWidget(self.file_scroll)

        left_layout.addWidget(file_list_frame, 2)

        # ---------------- RIGHT PANEL ----------------
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        title_right = QLabel("Result Display")
        title_right.setObjectName("SectionLabel")
        right_layout.addWidget(title_right)

        tab_container = QFrame()
        tab_container.setObjectName("TabContainer")
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        tab_buttons_layout = QHBoxLayout()
        tab_buttons_layout.setContentsMargins(0, 0, 0, 0)
        tab_buttons_layout.setSpacing(0)

        self.tab1_btn = QPushButton("Markdown Render Preview")
        self.tab2_btn = QPushButton("Markdown Raw Text")

        for btn in (self.tab1_btn, self.tab2_btn):
            btn.setObjectName("TabButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setMinimumHeight(32)
            tab_buttons_layout.addWidget(btn, 1)

        self.tab1_btn.setChecked(True)
        tab_layout.addLayout(tab_buttons_layout)

        self.tab_stack = QStackedWidget()

        # ✅ Tab 1: Rendered Markdown với Loading và Empty State
        tab1_container = QFrame()
        tab1_container.setObjectName("ResultBox")
        tab1_main_layout = QVBoxLayout(tab1_container)
        tab1_main_layout.setContentsMargins(0, 0, 0, 0)
        tab1_main_layout.setSpacing(0)

        # Empty state label (hiển thị khi chưa xử lý)
        self.empty_state_tab1 = QLabel("No content yet. Start processing to see results.")
        self.empty_state_tab1.setObjectName("EmptyStateLabel")
        self.empty_state_tab1.setAlignment(Qt.AlignCenter)
        self.empty_state_tab1.setWordWrap(True)
        tab1_main_layout.addWidget(self.empty_state_tab1)

        # Loading overlay (hiển thị khi đang xử lý)
        self.loading_overlay_tab1 = QLabel(tab1_container)
        self.loading_overlay_tab1.setAlignment(Qt.AlignCenter)
        self.loading_overlay_tab1.raise_()
        self.loading_overlay_tab1.hide()

        # Markdown preview (hiển thị khi có kết quả)
        self.markdown_preview = QTextBrowser()
        self.markdown_preview.setObjectName("ResultContent")
        self.markdown_preview.hide()  # Ẩn ban đầu
        tab1_main_layout.addWidget(self.markdown_preview)

        # Setup loading animation cho tab 1
        loading_gif_path = self.project_root / "assets" / "gif" / "loading.gif"
        if loading_gif_path.exists():
            self.loading_movie = QMovie(str(loading_gif_path))
            self.loading_movie.setScaledSize(QSize(200, 200))
            self.loading_overlay_tab1.setMovie(self.loading_movie)

        self.tab_stack.addWidget(tab1_container)

        # ✅ Tab 2: Raw Text (Editable) với Loading và Empty State
        tab2_container = QFrame()
        tab2_container.setObjectName("ResultBox")
        tab2_main_layout = QVBoxLayout(tab2_container)
        tab2_main_layout.setContentsMargins(0, 0, 0, 0)
        tab2_main_layout.setSpacing(0)

        # Empty state label (hiển thị khi chưa xử lý)
        self.empty_state_tab2 = QLabel("No content yet. Start processing to see results.")
        self.empty_state_tab2.setObjectName("EmptyStateLabel")
        self.empty_state_tab2.setAlignment(Qt.AlignCenter)
        self.empty_state_tab2.setWordWrap(True)
        tab2_main_layout.addWidget(self.empty_state_tab2)

        # Loading overlay (hiển thị khi đang xử lý)
        self.loading_overlay_tab2 = QLabel(tab2_container)
        self.loading_overlay_tab2.setAlignment(Qt.AlignCenter)
        self.loading_overlay_tab2.raise_()
        self.loading_overlay_tab2.hide()

        if loading_gif_path.exists():
            self.loading_movie_tab2 = QMovie(str(loading_gif_path))
            self.loading_movie_tab2.setScaledSize(QSize(200, 80))
            self.loading_overlay_tab2.setMovie(self.loading_movie_tab2)

        # Raw text area (hiển thị khi có kết quả)
        self.raw_text_area = QTextEdit()
        self.raw_text_area.setObjectName("ResultContent")
        self.raw_text_area.setAcceptRichText(False)
        self.raw_text_area.hide()  # Ẩn ban đầu
        tab2_main_layout.addWidget(self.raw_text_area)

        self.tab_stack.addWidget(tab2_container)

        tab_layout.addWidget(self.tab_stack)

        self.tab1_btn.clicked.connect(lambda: self._switch_tab(0))
        self.tab2_btn.clicked.connect(lambda: self._switch_tab(1))
        right_layout.addWidget(tab_container)

        # Gộp hai panel
        body_layout.addWidget(left_panel, 3)
        body_layout.addWidget(right_panel, 7)
        layout.addWidget(body_container, 1)

        # =====================================================
        #                     FOOTER
        # =====================================================
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 10, 0, 0)
        footer.setSpacing(10)

        # Buttons
        self.back_btn = QPushButton("Back")
        self.back_btn.setObjectName("FooterButton")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(lambda: self.navigate_back_requested.emit())

        self.stop_btn = QPushButton("Stop OCR")
        self.stop_btn.setObjectName("FooterStopButton")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.clicked.connect(self._stop_ocr)
        self.stop_btn.setEnabled(False)

        self.save_as_btn = QPushButton("Save As")
        self.save_as_btn.setObjectName("FooterSaveAsButton")
        self.save_as_btn.setCursor(Qt.PointingHandCursor)
        self.save_as_btn.clicked.connect(self._save_as)
        self.save_as_btn.setEnabled(False)

        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("FooterSaveButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_changes)
        self.save_btn.setEnabled(False)

        left_group = QHBoxLayout()
        left_group.setSpacing(8)
        left_group.addWidget(self.back_btn)
        left_group.addWidget(self.stop_btn)
        footer.addLayout(left_group)
        footer.addStretch(1)
        footer.addWidget(self.save_as_btn, alignment=Qt.AlignRight)
        footer.addWidget(self.save_btn, alignment=Qt.AlignRight)
        layout.addLayout(footer)

    # =====================================================
    #                     LOGIC
    # =====================================================
    def _switch_tab(self, index: int):
        self.tab_stack.setCurrentIndex(index)
        self.tab1_btn.setChecked(index == 0)
        self.tab2_btn.setChecked(index == 1)

    def _show_loading(self):
        """Hiển thị loading animation và ẩn empty state + content"""
        # Tab 1
        self.empty_state_tab1.hide()
        self.markdown_preview.hide()
        self.loading_overlay_tab1.setGeometry(self.loading_overlay_tab1.parent().rect())
        self.loading_overlay_tab1.show()
        if hasattr(self, 'loading_movie'):
            self.loading_movie.start()

        # Tab 2
        self.empty_state_tab2.hide()
        self.raw_text_area.hide()
        self.loading_overlay_tab2.setGeometry(self.loading_overlay_tab2.parent().rect())
        self.loading_overlay_tab2.show()
        if hasattr(self, 'loading_movie_tab2'):
            self.loading_movie_tab2.start()

    def _hide_loading(self):
        """Ẩn loading animation và hiển thị content"""
        # Tab 1
        self.loading_overlay_tab1.hide()
        if hasattr(self, 'loading_movie'):
            self.loading_movie.stop()
        self.markdown_preview.show()

        # Tab 2
        self.loading_overlay_tab2.hide()
        if hasattr(self, 'loading_movie_tab2'):
            self.loading_movie_tab2.stop()
        self.raw_text_area.show()

    def _show_empty_state(self):
        """Hiển thị empty state và ẩn loading + content"""
        # Tab 1
        self.loading_overlay_tab1.hide()
        if hasattr(self, 'loading_movie'):
            self.loading_movie.stop()
        self.markdown_preview.hide()
        self.empty_state_tab1.show()

        # Tab 2
        self.loading_overlay_tab2.hide()
        if hasattr(self, 'loading_movie_tab2'):
            self.loading_movie_tab2.stop()
        self.raw_text_area.hide()
        self.empty_state_tab2.show()

    def resizeEvent(self, event):
        """Đảm bảo loading overlay luôn ở giữa khi resize"""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay_tab1') and self.loading_overlay_tab1.isVisible():
            parent = self.loading_overlay_tab1.parent()
            if parent:
                self.loading_overlay_tab1.setGeometry(parent.rect())
        if hasattr(self, 'loading_overlay_tab2') and self.loading_overlay_tab2.isVisible():
            parent = self.loading_overlay_tab2.parent()
            if parent:
                self.loading_overlay_tab2.setGeometry(parent.rect())

    def load_files(self, files: list[Path], output_root: Path = None):
        """Hiển thị danh sách file và tự động bắt đầu xử lý"""
        self.clear_files()
        self.files = files
        self.file_items = []

        for idx, f in enumerate(files, start=1):
            row = FileRowItem(idx, f.name, "waiting", self.project_root)
            self.file_container_layout.addWidget(row)
            self.file_items.append(row)

        if files:
            self._show_preview(0)

        if output_root is None:
            output_root = self.project_root / "data" / "output"

        self._start_processing(files, output_root)

    def clear_files(self):
        """Xóa toàn bộ hàng file hiện tại"""
        while self.file_container_layout.count():
            item = self.file_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.file_items = []

    def _show_preview(self, index: int):
        """Hiển thị preview của file tại index"""
        if 0 <= index < len(self.files):
            file_path = self.files[index]
            try:
                pixmap = QPixmap(str(file_path))
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        self.preview_box.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.preview_box.setPixmap(scaled)
                    self.current_preview_index = index
            except Exception as e:
                logger.error(f"Error loading preview: {e}")

    def _start_processing(self, files: list[Path], output_root: Path):
        """Bắt đầu xử lý OCR với worker thread"""
        if self.worker and self.worker.isRunning():
            logger.warning("OCR is already running!")
            return

        # ✅ Hiển thị loading (ẩn empty state)
        self._show_loading()

        self.worker = OCRWorker(files, output_root)
        self.worker.progress.connect(self._on_progress)
        self.worker.result.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_finished)

        self.stop_btn.setEnabled(True)
        self.worker.start()

        logger.info(f"Started OCR processing for {len(files)} files")

    def _stop_ocr(self):
        """Dừng xử lý OCR"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.stop_btn.setEnabled(False)
            # ✅ Quay về empty state khi dừng
            self._show_empty_state()
            logger.info("OCR processing stopped by user")

    def _on_progress(self, index: int, status: str):
        """Callback khi status thay đổi"""
        if 0 <= index < len(self.file_items):
            self.file_items[index].update_status(status)
            if status == "processing":
                self._show_preview(index)

    def _on_result(self, index: int, markdown_text: str, processed_image: str):
        """Callback khi có kết quả OCR"""
        logger.info(f"Received result for file {index + 1}")

        # ✅ Ẩn loading và hiển thị content
        self._hide_loading()

        # ✅ Convert Markdown -> HTML để render đẹp hơn (có bảng, xuống dòng)
        html = markdown.markdown(markdown_text, extensions=["tables", "fenced_code", "nl2br"])
        self.markdown_preview.setHtml(html)

        # Raw text giữ nguyên (có thể edit)
        self.raw_text_area.setPlainText(markdown_text)

        # Hiển thị processed image
        if Path(processed_image).exists():
            pixmap = QPixmap(processed_image)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.preview_box.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_box.setPixmap(scaled)

        self.save_btn.setEnabled(True)
        self.save_as_btn.setEnabled(True)

    def _on_error(self, index: int, error_msg: str):
        """Callback khi có lỗi"""
        logger.error(f"Error processing file {index + 1}: {error_msg}")
        # Không ẩn loading ngay khi có lỗi, vì có thể còn file khác đang xử lý

    def _on_finished(self):
        """Callback khi hoàn thành tất cả"""
        # ✅ Nếu không có kết quả nào thành công, hiển thị empty state
        completed = sum(1 for item in self.file_items if item.current_state == "completed")
        
        if completed == 0:
            self._show_empty_state()
        else:
            # Nếu có kết quả, đã được hiển thị trong _on_result
            self._hide_loading()

        self.stop_btn.setEnabled(False)
        failed = sum(1 for item in self.file_items if item.current_state == "failed")
        logger.info(f"OCR processing complete: {completed} succeeded, {failed} failed")

    def _save_changes(self):
        """Lưu thay đổi từ raw text area"""
        # ✅ Lấy nội dung đã chỉnh sửa từ QTextEdit
        edited_text = self.raw_text_area.toPlainText()
        logger.info("Save button clicked - saving edited markdown content")
        
        # TODO: Implement logic để lưu edited_text vào file markdown
        # Ví dụ: 
        # if self.current_preview_index >= 0 and self.current_preview_index < len(self.files):
        #     file_path = self.files[self.current_preview_index]
        #     img_name = file_path.stem
        #     md_path = output_root / img_name / "text" / f"{img_name}_processed.md"
        #     md_path.write_text(edited_text, encoding="utf-8")

    def _save_as(self):
        """Lưu vào vị trí khác"""
        from PySide6.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select folder to save")
        if folder:
            logger.info(f"Save As to: {folder}")
            # ✅ Lấy nội dung đã chỉnh sửa
            edited_text = self.raw_text_area.toPlainText()
            # TODO: Implement save as logic với edited_text