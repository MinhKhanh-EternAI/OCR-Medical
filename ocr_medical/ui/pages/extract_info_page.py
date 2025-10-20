from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QStackedWidget, QScrollArea, QWidget, QTextBrowser, QSizePolicy, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QSize, QThread
from PySide6.QtGui import QPixmap, QMovie
from pathlib import Path
import logging
import markdown

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
    error = Signal(int, str)

    def __init__(self, files: list[Path], output_root: Path):
        super().__init__()
        self.files = files
        self.output_root = output_root
        self._is_running = True

    def run(self):
        for idx, file_path in enumerate(self.files):
            if not self._is_running:
                break
            try:
                self.progress.emit(idx, "processing")
                logger.info(f"Processing file {idx + 1}/{len(self.files)}: {file_path.name}")
                process_input(str(file_path), str(self.output_root))

                img_name = file_path.stem
                md_path = self.output_root / img_name / "text" / f"{img_name}_processed.md"
                processed_img = self.output_root / img_name / "processed" / f"{img_name}_processed.png"

                markdown_text = ""
                if md_path.exists():
                    markdown_text = md_path.read_text(encoding="utf-8")

                self.result.emit(idx, markdown_text, str(processed_img))
                self.progress.emit(idx, "completed")

            except Exception as e:
                self.error.emit(idx, str(e))
                self.progress.emit(idx, "failed")

        self.finished.emit()

    def stop(self):
        self._is_running = False


# =====================================================
#           File Row Item (Clickable)
# =====================================================
class FileRowItem(QFrame):
    clicked = Signal(int)

    def __init__(self, index: int, file_name: str, state: str, project_root: Path):
        super().__init__()
        self.setObjectName("FileRowItem")
        self.project_root = project_root
        self.index = index - 1
        self.current_state = state

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(0)

        # Cột 1: index
        idx_lbl = QLabel(str(index))
        idx_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(idx_lbl, 1)

        # Cột 2: tên file
        name_lbl = QLabel(file_name)
        layout.addWidget(name_lbl, 5)

        # Cột 3: trạng thái
        self.status_container = QWidget()
        self.status_layout = QHBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status_container, 3)

        self.update_status(state)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event)

    def update_status(self, state: str):
        """Cập nhật hiển thị trạng thái"""
        self.current_state = state
        while self.status_layout.count():
            item = self.status_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
        txt_lbl = QLabel(text)
        txt_lbl.setStyleSheet(f"color: {color}; font-weight: 500;")

        self.status_layout.addWidget(icon_lbl)
        self.status_layout.addWidget(txt_lbl)
        self.status_layout.addStretch()


# =====================================================
#              Extract Info Page
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
        self.results_cache = {}  # {index: (markdown_text, processed_img)}
        self.worker = None
        self.current_preview_index = 0

        layout = self.layout()
        layout.setSpacing(6)

        # ================= HEADER =================
        layout.removeWidget(self.header)
        layout.removeWidget(self.divider)
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.header, 1)
        layout.insertLayout(0, header_layout)
        layout.insertWidget(1, self.divider)

        # ================= BODY =================
        body_container = QFrame()
        body_container.setObjectName("BodyContainer")
        body_layout = QHBoxLayout(body_container)
        body_layout.setSpacing(12)
        body_layout.setContentsMargins(4, 6, 4, 0)

        # -------- LEFT PANEL --------
        left_panel = QFrame()
        left_panel.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        lbl = QLabel("File Preview")
        lbl.setObjectName("SectionLabel")
        left_layout.addWidget(lbl)

        self.preview_box = QLabel()
        self.preview_box.setObjectName("PreviewBox")
        self.preview_box.setAlignment(Qt.AlignCenter)
        self.preview_box.setScaledContents(False)
        self.preview_box.setMinimumSize(300, 200)
        self.preview_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        no_img = self.project_root / "assets" / "icon" / "no_image.svg"
        if no_img.exists():
            icon = load_svg_colored(no_img, self.theme_data["color"]["text"]["muted"], 100)
            self.preview_box.setPixmap(icon.pixmap(QSize(100, 100)))
        left_layout.addWidget(self.preview_box, 4)

        # ---- File list ----
        file_frame = QFrame()
        file_frame.setObjectName("FileListFrame")
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(0)

        header_row = QFrame()
        header_row.setObjectName("FileListHeader")
        h_layout = QHBoxLayout(header_row)
        h_layout.setContentsMargins(0, 6, 0, 6)
        for text, stretch in [("#", 1), ("File Name", 5), ("Status", 3)]:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)
            h_layout.addWidget(lbl, stretch)
        file_layout.addWidget(header_row)

        self.file_scroll = QScrollArea()
        self.file_scroll.setObjectName("FileScroll")
        self.file_scroll.setWidgetResizable(True)
        self.file_container = QWidget()
        self.file_container.setObjectName("FileListContainer")
        self.file_container_layout = QVBoxLayout(self.file_container)
        self.file_container_layout.setAlignment(Qt.AlignTop)
        self.file_container_layout.setContentsMargins(0, 0, 0, 0)
        self.file_scroll.setWidget(self.file_container)
        file_layout.addWidget(self.file_scroll)
        left_layout.addWidget(file_frame, 2)

        # -------- RIGHT PANEL --------
        right_panel = QFrame()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Result Display")
        lbl.setObjectName("SectionLabel")
        right_layout.addWidget(lbl)

        # Tabs
        tab_container = QFrame()
        tab_container.setObjectName("TabContainer")
        tab_layout = QVBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        # Tab buttons
        tab_btns = QHBoxLayout()
        tab_btns.setSpacing(0)
        self.tab1_btn = QPushButton("Markdown Render Preview")
        self.tab2_btn = QPushButton("Markdown Raw Text")
        for btn in (self.tab1_btn, self.tab2_btn):
            btn.setObjectName("TabButton")
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setCursor(Qt.PointingHandCursor)
            tab_btns.addWidget(btn, 1)
        self.tab1_btn.setChecked(True)
        tab_layout.addLayout(tab_btns)

        self.tab_stack = QStackedWidget()

        # ---- Tab 1: Markdown render ----
        tab1 = QFrame()
        tab1.setObjectName("ResultBox")
        t1_layout = QVBoxLayout(tab1)
        t1_layout.setContentsMargins(0, 0, 0, 0)
        t1_layout.setSpacing(0)

        self.empty_state_tab1 = QLabel("No content yet. Start processing to see results.")
        self.empty_state_tab1.setObjectName("EmptyStateLabel")
        self.empty_state_tab1.setAlignment(Qt.AlignCenter)
        t1_layout.addWidget(self.empty_state_tab1)

        # ✅ Loading căn giữa tab 1
        self.loading_overlay_tab1 = QLabel(tab1)
        self.loading_overlay_tab1.setAlignment(Qt.AlignCenter)
        self.loading_overlay_tab1.setAttribute(Qt.WA_TranslucentBackground)
        self.loading_overlay_tab1.setStyleSheet(
            "background-color: rgba(255, 255, 255, 180); border-radius: 8px;"
        )
        self.loading_overlay_tab1.hide()
        t1_layout.addWidget(self.loading_overlay_tab1, alignment=Qt.AlignCenter)

        self.markdown_preview = QTextBrowser()
        self.markdown_preview.setObjectName("ResultContent")
        self.markdown_preview.hide()
        t1_layout.addWidget(self.markdown_preview)
        self.tab_stack.addWidget(tab1)

        # ---- Tab 2: Raw text ----
        tab2 = QFrame()
        tab2.setObjectName("ResultBox")
        t2_layout = QVBoxLayout(tab2)
        t2_layout.setContentsMargins(0, 0, 0, 0)
        t2_layout.setSpacing(0)

        self.empty_state_tab2 = QLabel("No content yet. Start processing to see results.")
        self.empty_state_tab2.setObjectName("EmptyStateLabel")
        self.empty_state_tab2.setAlignment(Qt.AlignCenter)
        t2_layout.addWidget(self.empty_state_tab2)

        # ✅ Loading căn giữa tab 2
        self.loading_overlay_tab2 = QLabel(tab2)
        self.loading_overlay_tab2.setAlignment(Qt.AlignCenter)
        self.loading_overlay_tab2.setAttribute(Qt.WA_TranslucentBackground)
        self.loading_overlay_tab2.setStyleSheet(
            "background-color: rgba(255, 255, 255, 180); border-radius: 8px;"
        )
        self.loading_overlay_tab2.hide()
        t2_layout.addWidget(self.loading_overlay_tab2, alignment=Qt.AlignCenter)

        self.raw_text_area = QTextEdit()
        self.raw_text_area.setObjectName("ResultContent")
        self.raw_text_area.setAcceptRichText(False)
        self.raw_text_area.setReadOnly(False)
        self.raw_text_area.hide()
        t2_layout.addWidget(self.raw_text_area)
        self.tab_stack.addWidget(tab2)

        tab_layout.addWidget(self.tab_stack)
        right_layout.addWidget(tab_container)
        self.tab1_btn.clicked.connect(lambda: self._switch_tab(0))
        self.tab2_btn.clicked.connect(lambda: self._switch_tab(1))

        body_layout.addWidget(left_panel, 3)
        body_layout.addWidget(right_panel, 7)
        layout.addWidget(body_container, 1)

        # ================= FOOTER =================
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 10, 0, 0)
        footer.setSpacing(10)
        self.back_btn = QPushButton("Back")
        self.back_btn.setObjectName("FooterButton")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(lambda: self.navigate_back_requested.emit())
        self.stop_btn = QPushButton("Stop OCR")
        self.stop_btn.setObjectName("FooterStopButton")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_ocr)
        self.save_as_btn = QPushButton("Save As")
        self.save_as_btn.setObjectName("FooterSaveAsButton")
        self.save_as_btn.setCursor(Qt.PointingHandCursor)
        self.save_as_btn.setEnabled(False)
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("FooterSaveButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setEnabled(False)
        footer.addWidget(self.back_btn)
        footer.addWidget(self.stop_btn)
        footer.addStretch()
        footer.addWidget(self.save_as_btn)
        footer.addWidget(self.save_btn)
        layout.addLayout(footer)

        # ✅ Loading gif căn giữa + scale cố định
        gif_path = self.project_root / "assets" / "gif" / "loading.gif"
        if gif_path.exists():
            self.loading_movie1 = QMovie(str(gif_path))
            self.loading_movie2 = QMovie(str(gif_path))
            self.loading_movie1.setScaledSize(QSize(400, 400))
            self.loading_movie2.setScaledSize(QSize(400, 400))
            self.loading_overlay_tab1.setMovie(self.loading_movie1)
            self.loading_overlay_tab2.setMovie(self.loading_movie2)
            self.loading_overlay_tab1.raise_()
            self.loading_overlay_tab2.raise_()

    # =====================================================
    #                   Logic
    # =====================================================
    def _switch_tab(self, idx: int):
        self.tab_stack.setCurrentIndex(idx)
        self.tab1_btn.setChecked(idx == 0)
        self.tab2_btn.setChecked(idx == 1)

    def _show_loading(self):
        """Hiện loading"""
        self.empty_state_tab1.hide()
        self.empty_state_tab2.hide()
        self.markdown_preview.hide()
        self.raw_text_area.hide()
        self.loading_overlay_tab1.show()
        self.loading_overlay_tab2.show()
        if hasattr(self, "loading_movie1"):
            self.loading_movie1.start()
        if hasattr(self, "loading_movie2"):
            self.loading_movie2.start()

    def _hide_loading(self):
        """Ẩn loading, hiển thị content"""
        self.loading_overlay_tab1.hide()
        self.loading_overlay_tab2.hide()
        if hasattr(self, "loading_movie1"):
            self.loading_movie1.stop()
        if hasattr(self, "loading_movie2"):
            self.loading_movie2.stop()
        self.empty_state_tab1.hide()
        self.empty_state_tab2.hide()
        self.markdown_preview.show()
        self.raw_text_area.show()
        self.raw_text_area.textChanged.connect(self._update_live_preview)

    def _update_live_preview(self):
        text = self.raw_text_area.toPlainText()
        html = markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
        self.markdown_preview.setHtml(html)

    def load_files(self, files: list[Path], output_root: Path = None):
        self.clear_files()
        self.files = files
        for idx, f in enumerate(files, start=1):
            row = FileRowItem(idx, f.name, "waiting", self.project_root)
            row.clicked.connect(self._on_file_clicked)
            self.file_container_layout.addWidget(row)
            self.file_items.append(row)
        if files:
            self._show_preview(0)
        if not output_root:
            output_root = self.project_root / "data" / "output"
        self._start_processing(files, output_root)

    def clear_files(self):
        while self.file_container_layout.count():
            item = self.file_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.file_items.clear()

    def _show_preview(self, idx: int, processed=False):
        if 0 <= idx < len(self.files):
            path = self.files[idx]
            if processed and idx in self.results_cache:
                _, img = self.results_cache[idx]
                path = Path(img)
            pix = QPixmap(str(path))
            if not pix.isNull():
                scaled = pix.scaled(self.preview_box.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_box.setPixmap(scaled)
                self.current_preview_index = idx

    def _on_file_clicked(self, idx: int):
        """Click vào dòng file"""
        state = self.file_items[idx].current_state
        if state == "processing":
            self._show_loading()
            self._show_preview(idx, processed=False)
        elif state == "completed" and idx in self.results_cache:
            self._hide_loading()
            md, img = self.results_cache[idx]
            html = markdown.markdown(md, extensions=["tables", "fenced_code", "nl2br"])
            self.markdown_preview.setHtml(html)
            self.raw_text_area.setPlainText(md)
            self._show_preview(idx, processed=True)
        elif state in ("waiting", "failed"):
            self._show_empty_state()
            self._show_preview(idx, processed=False)

    def _start_processing(self, files, out_root):
        if self.worker and self.worker.isRunning():
            return
        self._show_loading()
        self.worker = OCRWorker(files, out_root)
        self.worker.progress.connect(self._on_progress)
        self.worker.result.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_finished)
        self.stop_btn.setEnabled(True)
        self.worker.start()

    def _on_progress(self, idx, status):
        self.file_items[idx].update_status(status)
        if status == "processing":
            self._show_preview(idx, processed=False)

    def _on_result(self, idx, text, img):
        self.results_cache[idx] = (text, img)
        self.file_items[idx].update_status("completed")
        self._hide_loading()
        html = markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
        self.markdown_preview.setHtml(html)
        self.raw_text_area.setPlainText(text)
        self._show_preview(idx, processed=True)
        self.save_btn.setEnabled(True)
        self.save_as_btn.setEnabled(True)

    def _on_error(self, idx, msg):
        self.file_items[idx].update_status("failed")
        logger.error(f"OCR error on file {idx}: {msg}")

    def _on_finished(self):
        self.stop_btn.setEnabled(False)
        logger.info("OCR worker finished.")

    def _stop_ocr(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self._show_empty_state()
            self.stop_btn.setEnabled(False)
            logger.info("OCR stopped by user.")

    def _show_empty_state(self):
        self.loading_overlay_tab1.hide()
        self.loading_overlay_tab2.hide()
        self.markdown_preview.hide()
        self.raw_text_area.hide()
        self.empty_state_tab1.show()
        self.empty_state_tab2.show()
