from __future__ import annotations

from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
    QStackedWidget, QScrollArea, QWidget, QTextBrowser, QSizePolicy, QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt, Signal, QSize, QThread
from PySide6.QtGui import QPixmap, QMovie
from pathlib import Path
import logging
import markdown
import json

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored

logger = logging.getLogger(__name__)


# =====================================================
#             OCR Worker Thread
# =====================================================
class OCRWorker(QThread):
    """Worker thread để xử lý OCR không block UI"""

    progress = Signal(int, str)  # (index, status)
    step_progress = Signal(int, str)  # (index, step: "load_model", "process_image", "extract_info", "success")
    result = Signal(int, str, str)  # (index, markdown_text, image_path)
    finished = Signal()
    error = Signal(int, str)
    stopped = Signal()  # Signal khi bị dừng

    def __init__(self, files: list[Path], output_root: Path, page_instance=None, file_indices: list[int] = None):
        super().__init__()
        self.files = files
        self.output_root = output_root
        self.page_instance = page_instance
        self.file_indices = file_indices  # Danh sách index của file cần xử lý
        self._is_running = True
        self._force_stop = False  # Flag để dừng ngay lập tức

    def run(self):
        from ocr_medical.core.waifu2x_loader import load_waifu2x
        from ocr_medical.core.process_image import process_image
        from ocr_medical.core.ocr_extract import call_qwen_ocr
        from PIL import Image
        
        try:
            # Xác định danh sách file cần xử lý
            if self.file_indices:
                files_to_process = [(idx, self.files[idx]) for idx in self.file_indices]
            else:
                files_to_process = list(enumerate(self.files))
            
            # Bước 1: Load model Waifu2x (chỉ load 1 lần)
            if len(files_to_process) > 0 and self._is_running:
                first_idx = files_to_process[0][0]
                self.step_progress.emit(first_idx, "load_model")
                upscaler = load_waifu2x()
            
            if not self._is_running:
                self.stopped.emit()
                return
            
            for i, (idx, file_path) in enumerate(files_to_process):
                # Kiểm tra force stop ở đầu mỗi vòng lặp
                if self._force_stop or not self._is_running:
                    logger.info(f"OCR stopped at file {idx}")
                    self.stopped.emit()
                    return
                
                try:
                    self.progress.emit(idx, "processing")
                    logger.info(f"Processing file {idx + 1}/{len(self.files)}: {file_path.name}")
                    
                    # Nếu không phải file đầu tiên, vẫn emit load_model nhưng nhanh hơn
                    if i > 0 and self._is_running:
                        self.step_progress.emit(idx, "load_model")
                        self.msleep(300)
                    
                    if not self._is_running:
                        self.stopped.emit()
                        return
                    
                    # Bước 2: Process image (upscale)
                    self.step_progress.emit(idx, "process_image")
                    img = Image.open(file_path).convert("RGB")
                    img_name = file_path.stem
                    _, processed_path = process_image(upscaler, img, img_name, self.output_root)
                    
                    if not self._is_running:
                        self.stopped.emit()
                        return
                    
                    # Bước 3: Extract information (OCR)
                    self.step_progress.emit(idx, "extract_info")
                    from ocr_medical.core.pipeline import DEFAULT_PROMPT
                    out_dir_text = self.output_root / img_name / "text"
                    out_dir_text.mkdir(parents=True, exist_ok=True)
                    
                    extracted = call_qwen_ocr(str(processed_path), DEFAULT_PROMPT)
                    
                    if not self._is_running:
                        self.stopped.emit()
                        return
                    
                    md_path = out_dir_text / f"{img_name}_processed.md"
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(extracted)

                    markdown_text = extracted
                    processed_img = self.output_root / img_name / "processed" / f"{img_name}_processed.png"

                    # Bước 4: Success
                    self.step_progress.emit(idx, "success")
                    self.msleep(1500)  # Hiển thị success 1.5 giây
                    
                    if not self._is_running:
                        self.stopped.emit()
                        return
                    
                    self.result.emit(idx, markdown_text, str(processed_img))
                    self.progress.emit(idx, "completed")

                except Exception as e:
                    if not self._is_running:
                        self.stopped.emit()
                        return
                    self.error.emit(idx, str(e))
                    self.progress.emit(idx, "failed")
                    logger.error(f"Error processing file {idx}: {str(e)}")

            self.finished.emit()
            
        except Exception as e:
            logger.error(f"OCR Worker crashed: {str(e)}")
            self.stopped.emit()

    def stop(self):
        """Dừng worker một cách an toàn"""
        self._is_running = False
        self._force_stop = True
        logger.info("OCR Worker stop requested")
    
    def terminate_worker(self):
        """Buộc dừng worker ngay lập tức (sử dụng trong trường hợp khẩn cấp)"""
        self._force_stop = True
        self._is_running = False
        self.terminate()  # Force terminate thread
        logger.warning("OCR Worker force terminated")


# =====================================================
#           File Row Item (Clickable)
# =====================================================
class FileRowItem(QFrame):
    clicked = Signal(int)
    reload_requested = Signal(int)

    def __init__(self, index: int, file_name: str, state: str, project_root: Path):
        super().__init__()
        self.setObjectName("FileRowItem")
        self.project_root = project_root
        self.index = index - 1
        self.current_state = state

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        # Cột 1: index - căn giữa (width: 50px)
        idx_container = QWidget()
        idx_container.setFixedWidth(50)
        idx_layout = QHBoxLayout(idx_container)
        idx_layout.setContentsMargins(0, 0, 0, 0)
        idx_layout.setAlignment(Qt.AlignCenter)
        idx_lbl = QLabel(str(index))
        idx_lbl.setAlignment(Qt.AlignCenter)
        idx_layout.addWidget(idx_lbl)
        layout.addWidget(idx_container)

        # Cột 2: tên file - căn trái
        name_lbl = QLabel(file_name)
        name_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(name_lbl, 1)

        # Cột 3: trạng thái - căn trái (width: 150px)
        self.status_container = QWidget()
        self.status_container.setFixedWidth(150)
        self.status_layout = QHBoxLayout(self.status_container)
        self.status_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.status_container)

        # Cột 4: action - căn giữa (width: 80px)
        action_container = QWidget()
        action_container.setFixedWidth(80)
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setAlignment(Qt.AlignCenter)
        
        self.reload_btn = QPushButton()
        self.reload_btn.setObjectName("ReloadButton")
        self.reload_btn.setFlat(True)
        self.reload_btn.setFixedSize(24, 24)
        self.reload_btn.setFocusPolicy(Qt.NoFocus)
        self.reload_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover:!disabled {
                background: rgba(107, 114, 128, 0.1);
                border-radius: 4px;
            }
            QPushButton:disabled {
                opacity: 0.5;
            }
        """)
        
        reload_icon_path = self.project_root / "assets" / "icon" / "reload.svg"
        if reload_icon_path.exists():
            reload_icon = load_svg_colored(reload_icon_path, "#6B7280", 16)
            self.reload_btn.setIcon(reload_icon)
            self.reload_btn.setIconSize(QSize(16, 16))
        
        self.reload_btn.clicked.connect(lambda: self.reload_requested.emit(self.index))
        action_layout.addWidget(self.reload_btn)
        layout.addWidget(action_container)

        self.update_status(state)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Chỉ emit clicked nếu không click vào reload button
            if not self.reload_btn.geometry().contains(event.pos()):
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
        
        # Vô hiệu hóa nút reload khi đang xử lý
        if state == "processing":
            self.reload_btn.setEnabled(False)
            self.reload_btn.setCursor(Qt.ForbiddenCursor)
        else:
            self.reload_btn.setEnabled(True)
            self.reload_btn.setCursor(Qt.PointingHandCursor)


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
        self.output_root = None
        self.file_items = []
        self.results_cache = {}
        self.file_status = {}
        self.file_md_paths = {}
        self.worker = None
        self.current_preview_index = 0
        
        # Load storage directory từ config
        self.storage_dir = self._load_storage_dir()

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
        h_layout.setContentsMargins(12, 6, 12, 6)
        h_layout.setSpacing(8)
        
        idx_header_container = QWidget()
        idx_header_container.setFixedWidth(50)
        idx_header_layout = QHBoxLayout(idx_header_container)
        idx_header_layout.setContentsMargins(0, 0, 0, 0)
        idx_header_layout.setAlignment(Qt.AlignCenter)
        idx_header = QLabel("#")
        idx_header.setAlignment(Qt.AlignCenter)
        idx_header_layout.addWidget(idx_header)
        h_layout.addWidget(idx_header_container)
        
        name_header = QLabel("File Name")
        name_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        h_layout.addWidget(name_header, 1)
        
        status_header_container = QWidget()
        status_header_container.setFixedWidth(150)
        status_header_layout = QHBoxLayout(status_header_container)
        status_header_layout.setContentsMargins(0, 0, 0, 0)
        status_header = QLabel("Status")
        status_header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        status_header_layout.addWidget(status_header)
        h_layout.addWidget(status_header_container)
        
        action_header_container = QWidget()
        action_header_container.setFixedWidth(80)
        action_header_layout = QHBoxLayout(action_header_container)
        action_header_layout.setContentsMargins(0, 0, 0, 0)
        action_header_layout.setAlignment(Qt.AlignCenter)
        action_header = QLabel("Action")
        action_header.setAlignment(Qt.AlignCenter)
        action_header_layout.addWidget(action_header)
        h_layout.addWidget(action_header_container)
        
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

        # Tạo stacked widget cho tab 1
        self.tab1_stack = QStackedWidget()
        
        # Page 1: Empty state
        empty_page_tab1 = QWidget()
        empty_layout_tab1 = QVBoxLayout(empty_page_tab1)
        empty_layout_tab1.setContentsMargins(0, 0, 0, 0)
        self.empty_state_tab1 = QLabel("No content yet. Start processing to see results.")
        self.empty_state_tab1.setObjectName("EmptyStateLabel")
        self.empty_state_tab1.setAlignment(Qt.AlignCenter)
        empty_layout_tab1.addWidget(self.empty_state_tab1)
        self.tab1_stack.addWidget(empty_page_tab1)

        # Page 2: Processing state
        processing_page_tab1 = QWidget()
        processing_layout_main_tab1 = QVBoxLayout(processing_page_tab1)
        processing_layout_main_tab1.setContentsMargins(0, 0, 0, 0)
        self.processing_container_tab1 = QFrame()
        self.processing_container_tab1.setObjectName("ProcessingContainer")
        processing_layout_tab1 = QVBoxLayout(self.processing_container_tab1)
        processing_layout_tab1.setAlignment(Qt.AlignCenter)
        processing_layout_tab1.setSpacing(10)
        
        self.processing_gif_tab1 = QLabel()
        self.processing_gif_tab1.setAlignment(Qt.AlignCenter)
        processing_layout_tab1.addWidget(self.processing_gif_tab1)
        
        self.processing_text_tab1 = QLabel()
        self.processing_text_tab1.setAlignment(Qt.AlignCenter)
        self.processing_text_tab1.setStyleSheet("font-size: 16px; font-weight: 500;")
        processing_layout_tab1.addWidget(self.processing_text_tab1)
        
        processing_layout_main_tab1.addWidget(self.processing_container_tab1, alignment=Qt.AlignCenter)
        self.tab1_stack.addWidget(processing_page_tab1)

        # Page 3: Content preview
        content_page_tab1 = QWidget()
        content_layout_tab1 = QVBoxLayout(content_page_tab1)
        content_layout_tab1.setContentsMargins(0, 0, 0, 0)
        self.markdown_preview = QTextBrowser()
        self.markdown_preview.setObjectName("ResultContent")
        content_layout_tab1.addWidget(self.markdown_preview)
        self.tab1_stack.addWidget(content_page_tab1)
        
        t1_layout.addWidget(self.tab1_stack)
        self.tab_stack.addWidget(tab1)

        # ---- Tab 2: Raw text ----
        tab2 = QFrame()
        tab2.setObjectName("ResultBox")
        t2_layout = QVBoxLayout(tab2)
        t2_layout.setContentsMargins(0, 0, 0, 0)
        t2_layout.setSpacing(0)

        # Tạo stacked widget cho tab 2
        self.tab2_stack = QStackedWidget()
        
        # Page 1: Empty state
        empty_page_tab2 = QWidget()
        empty_layout_tab2 = QVBoxLayout(empty_page_tab2)
        empty_layout_tab2.setContentsMargins(0, 0, 0, 0)
        self.empty_state_tab2 = QLabel("No content yet. Start processing to see results.")
        self.empty_state_tab2.setObjectName("EmptyStateLabel")
        self.empty_state_tab2.setAlignment(Qt.AlignCenter)
        empty_layout_tab2.addWidget(self.empty_state_tab2)
        self.tab2_stack.addWidget(empty_page_tab2)

        # Page 2: Processing state
        processing_page_tab2 = QWidget()
        processing_layout_main_tab2 = QVBoxLayout(processing_page_tab2)
        processing_layout_main_tab2.setContentsMargins(0, 0, 0, 0)
        self.processing_container_tab2 = QFrame()
        self.processing_container_tab2.setObjectName("ProcessingContainer")
        processing_layout_tab2 = QVBoxLayout(self.processing_container_tab2)
        processing_layout_tab2.setAlignment(Qt.AlignCenter)
        processing_layout_tab2.setSpacing(10)
        
        self.processing_gif_tab2 = QLabel()
        self.processing_gif_tab2.setAlignment(Qt.AlignCenter)
        processing_layout_tab2.addWidget(self.processing_gif_tab2)
        
        self.processing_text_tab2 = QLabel()
        self.processing_text_tab2.setAlignment(Qt.AlignCenter)
        self.processing_text_tab2.setStyleSheet("font-size: 16px; font-weight: 500;")
        processing_layout_tab2.addWidget(self.processing_text_tab2)
        
        processing_layout_main_tab2.addWidget(self.processing_container_tab2, alignment=Qt.AlignCenter)
        self.tab2_stack.addWidget(processing_page_tab2)

        # Page 3: Content editor
        content_page_tab2 = QWidget()
        content_layout_tab2 = QVBoxLayout(content_page_tab2)
        content_layout_tab2.setContentsMargins(0, 0, 0, 0)
        self.raw_text_area = QTextEdit()
        self.raw_text_area.setObjectName("ResultContent")
        self.raw_text_area.setAcceptRichText(False)
        self.raw_text_area.setReadOnly(False)
        self.raw_text_area.setPlaceholderText("Edit markdown content here...")
        self.raw_text_area.setFocusPolicy(Qt.StrongFocus)
        self.raw_text_area.setEnabled(True)
        self.raw_text_area.viewport().setCursor(Qt.IBeamCursor)
        self.raw_text_area.setCursor(Qt.IBeamCursor)
        self.raw_text_area.setTextInteractionFlags(Qt.TextEditorInteraction)
        content_layout_tab2.addWidget(self.raw_text_area)
        self.tab2_stack.addWidget(content_page_tab2)
        
        t2_layout.addWidget(self.tab2_stack)
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
        self.save_as_btn.clicked.connect(self._save_as_markdown)
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("FooterSaveButton")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_markdown)
        footer.addWidget(self.back_btn)
        footer.addWidget(self.stop_btn)
        footer.addStretch()
        footer.addWidget(self.save_as_btn)
        footer.addWidget(self.save_btn)
        layout.addLayout(footer)

        # Load các GIF movies
        self._load_gif_movies()

    def _load_gif_movies(self):
        """Load tất cả các GIF cần thiết"""
        gif_size = QSize(300, 300)
        
        # Loading GIF (cho bước 3)
        loading_path = self.project_root / "assets" / "gif" / "loading.gif"
        if loading_path.exists():
            self.loading_movie_tab1 = QMovie(str(loading_path))
            self.loading_movie_tab2 = QMovie(str(loading_path))
            self.loading_movie_tab1.setScaledSize(gif_size)
            self.loading_movie_tab2.setScaledSize(gif_size)
        
        # Image GIF (cho bước 1 và 2)
        image_path = self.project_root / "assets" / "gif" / "image.gif"
        if image_path.exists():
            self.image_movie_tab1 = QMovie(str(image_path))
            self.image_movie_tab2 = QMovie(str(image_path))
            self.image_movie_tab1.setScaledSize(gif_size)
            self.image_movie_tab2.setScaledSize(gif_size)
        
        # Waiting GIF
        waiting_path = self.project_root / "assets" / "gif" / "waiting.gif"
        if waiting_path.exists():
            self.waiting_movie_tab1 = QMovie(str(waiting_path))
            self.waiting_movie_tab2 = QMovie(str(waiting_path))
            self.waiting_movie_tab1.setScaledSize(gif_size)
            self.waiting_movie_tab2.setScaledSize(gif_size)
        
        # Error GIF
        error_path = self.project_root / "assets" / "gif" / "error.gif"
        if error_path.exists():
            self.error_movie_tab1 = QMovie(str(error_path))
            self.error_movie_tab2 = QMovie(str(error_path))
            self.error_movie_tab1.setScaledSize(gif_size)
            self.error_movie_tab2.setScaledSize(gif_size)
        
        # Success GIF
        success_path = self.project_root / "assets" / "gif" / "success.gif"
        if success_path.exists():
            self.success_movie_tab1 = QMovie(str(success_path))
            self.success_movie_tab2 = QMovie(str(success_path))
            self.success_movie_tab1.setScaledSize(gif_size)
            self.success_movie_tab2.setScaledSize(gif_size)

    # =====================================================
    #                   Logic
    # =====================================================
    def _load_storage_dir(self) -> Path:
        """Load storage directory từ config file"""
        config_path = self.project_root / "config" / "app_config.json"
        
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    storage_path_str = config.get("storage_path", "").strip()
                    if storage_path_str:
                        custom_dir = Path(storage_path_str)
                        if custom_dir.exists():
                            logger.info(f"Using custom storage path: {custom_dir}")
                            return custom_dir
                        else:
                            logger.warning(f"Storage_path không tồn tại: {custom_dir}")
            
            # Nếu không có config hoặc storage_dir rỗng, dùng AppData mặc định
            from PySide6.QtCore import QStandardPaths
            app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            default_path = Path(app_data) / "OCR-Medical" / "output"
            default_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using default AppData directory: {default_path}")
            return default_path
            
        except Exception as e:
            logger.error(f"Error loading storage directory from config: {str(e)}")
            fallback_path = self.project_root / "data" / "output"
            fallback_path.mkdir(parents=True, exist_ok=True)
            return fallback_path

    def _switch_tab(self, idx: int):
        self.tab_stack.setCurrentIndex(idx)
        self.tab1_btn.setChecked(idx == 0)
        self.tab2_btn.setChecked(idx == 1)

    def _show_processing_step(self, step: str):
        """Hiển thị từng bước xử lý với GIF và text tương ứng"""
        # Chuyển sang page processing (index 1)
        self.tab1_stack.setCurrentIndex(1)
        self.tab2_stack.setCurrentIndex(1)
        
        # Stop tất cả movies trước
        self._stop_all_movies()
        
        if step == "load_model":
            # Bước 1: Loading model
            if hasattr(self, "image_movie_tab1"):
                self.processing_gif_tab1.setMovie(self.image_movie_tab1)
                self.image_movie_tab1.start()
            if hasattr(self, "image_movie_tab2"):
                self.processing_gif_tab2.setMovie(self.image_movie_tab2)
                self.image_movie_tab2.start()
            self.processing_text_tab1.setText("Loading model (1/3)")
            self.processing_text_tab2.setText("Loading model (1/3)")
            
        elif step == "process_image":
            # Bước 2: Processing image
            if hasattr(self, "image_movie_tab1"):
                self.processing_gif_tab1.setMovie(self.image_movie_tab1)
                self.image_movie_tab1.start()
            if hasattr(self, "image_movie_tab2"):
                self.processing_gif_tab2.setMovie(self.image_movie_tab2)
                self.image_movie_tab2.start()
            self.processing_text_tab1.setText("Processing image (2/3)")
            self.processing_text_tab2.setText("Processing image (2/3)")
            
        elif step == "extract_info":
            # Bước 3: Extracting information
            if hasattr(self, "loading_movie_tab1"):
                self.processing_gif_tab1.setMovie(self.loading_movie_tab1)
                self.loading_movie_tab1.start()
            if hasattr(self, "loading_movie_tab2"):
                self.processing_gif_tab2.setMovie(self.loading_movie_tab2)
                self.loading_movie_tab2.start()
            self.processing_text_tab1.setText("Extracting information (3/3)")
            self.processing_text_tab2.setText("Extracting information (3/3)")
            
        elif step == "success":
            # Bước 4: Success
            if hasattr(self, "success_movie_tab1"):
                self.processing_gif_tab1.setMovie(self.success_movie_tab1)
                self.success_movie_tab1.start()
            if hasattr(self, "success_movie_tab2"):
                self.processing_gif_tab2.setMovie(self.success_movie_tab2)
                self.success_movie_tab2.start()
            
            # Đếm số file đã completed
            completed_count = sum(1 for status in self.file_status.values() if status == "completed")
            total_count = len(self.files)
            self.processing_text_tab1.setText(f"Success! Extracted {completed_count}/{total_count} file(s)")
            self.processing_text_tab2.setText(f"Success! Extracted {completed_count}/{total_count} file(s)")

    def _show_waiting_state(self):
        """Hiển thị trạng thái chờ xử lý"""
        # Chuyển sang page processing (index 1)
        self.tab1_stack.setCurrentIndex(1)
        self.tab2_stack.setCurrentIndex(1)
        
        self._stop_all_movies()
        
        if hasattr(self, "waiting_movie_tab1"):
            self.processing_gif_tab1.setMovie(self.waiting_movie_tab1)
            self.waiting_movie_tab1.start()
        if hasattr(self, "waiting_movie_tab2"):
            self.processing_gif_tab2.setMovie(self.waiting_movie_tab2)
            self.waiting_movie_tab2.start()
        
        self.processing_text_tab1.setText("Waiting for processing...")
        self.processing_text_tab2.setText("Waiting for processing...")

    def _show_error_state(self):
        """Hiển thị trạng thái lỗi"""
        # Chuyển sang page processing (index 1)
        self.tab1_stack.setCurrentIndex(1)
        self.tab2_stack.setCurrentIndex(1)
        
        self._stop_all_movies()
        
        if hasattr(self, "error_movie_tab1"):
            self.processing_gif_tab1.setMovie(self.error_movie_tab1)
            self.error_movie_tab1.start()
        if hasattr(self, "error_movie_tab2"):
            self.processing_gif_tab2.setMovie(self.error_movie_tab2)
            self.error_movie_tab2.start()
        
        self.processing_text_tab1.setText("Error occurred. Please try again.")
        self.processing_text_tab2.setText("Error occurred. Please try again.")

    def _stop_all_movies(self):
        """Dừng tất cả các GIF movies"""
        for attr in ["loading_movie_tab1", "loading_movie_tab2", 
                     "image_movie_tab1", "image_movie_tab2",
                     "waiting_movie_tab1", "waiting_movie_tab2",
                     "error_movie_tab1", "error_movie_tab2",
                     "success_movie_tab1", "success_movie_tab2"]:
            if hasattr(self, attr):
                movie = getattr(self, attr)
                if movie.state() == QMovie.Running:
                    movie.stop()

    def _show_result_content(self):
        """Hiển thị kết quả OCR"""
        # Chuyển sang page content (index 2)
        self.tab1_stack.setCurrentIndex(2)
        self.tab2_stack.setCurrentIndex(2)
        
        self._stop_all_movies()
        
        # Đảm bảo raw_text_area có thể nhận focus và tương tác
        self.raw_text_area.setReadOnly(False)
        self.raw_text_area.setEnabled(True)
        self.raw_text_area.setFocusPolicy(Qt.StrongFocus)
        
        # Kết nối signal để cập nhật live preview khi chỉnh sửa
        try:
            self.raw_text_area.textChanged.disconnect(self._update_live_preview)
        except:
            pass
        self.raw_text_area.textChanged.connect(self._update_live_preview)

    def _show_empty_state(self):
        """Hiển thị trạng thái rỗng"""
        # Chuyển sang page empty (index 0)
        self.tab1_stack.setCurrentIndex(0)
        self.tab2_stack.setCurrentIndex(0)
        self._stop_all_movies()

    def _update_live_preview(self):
        """Cập nhật markdown preview khi chỉnh sửa raw text"""
        text = self.raw_text_area.toPlainText()
        html = markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
        self.markdown_preview.setHtml(html)
        
        # Cập nhật cache với nội dung mới
        if self.current_preview_index in self.results_cache:
            _, img_path = self.results_cache[self.current_preview_index]
            self.results_cache[self.current_preview_index] = (text, img_path)

    def _save_markdown(self):
        """Lưu nội dung markdown hiện tại vào file gốc"""
        idx = self.current_preview_index
        
        if idx not in self.file_md_paths:
            logger.warning(f"No markdown file path for index {idx}")
            return
        
        md_path = self.file_md_paths[idx]
        text = self.raw_text_area.toPlainText()
        
        try:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"Saved markdown to: {md_path}")
            
            # Cập nhật cache
            if idx in self.results_cache:
                _, img_path = self.results_cache[idx]
                self.results_cache[idx] = (text, img_path)
                
        except Exception as e:
            logger.error(f"Error saving markdown: {str(e)}")

    def _save_as_markdown(self):
        """Lưu nội dung markdown vào file mới"""
        text = self.raw_text_area.toPlainText()
        
        # Sử dụng storage_dir làm thư mục mặc định
        default_dir = str(self.storage_dir) if self.storage_dir else str(self.output_root)
        
        # Mở dialog để chọn vị trí lưu
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Markdown As",
            default_dir,
            "Markdown Files (*.md)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                logger.info(f"Saved markdown to: {file_path}")
            except Exception as e:
                logger.error(f"Error saving markdown: {str(e)}")

    def load_files(self, files: list[Path], output_root: Path = None):
        """Load danh sách files và bắt đầu xử lý"""
        self.clear_files()
        self.files = files
        self.file_status = {}
        self.file_md_paths = {}
        
        for idx, f in enumerate(files, start=1):
            row = FileRowItem(idx, f.name, "waiting", self.project_root)
            row.clicked.connect(self._on_file_clicked)
            row.reload_requested.connect(self._on_reload_requested)
            self.file_container_layout.addWidget(row)
            self.file_items.append(row)
            self.file_status[idx - 1] = "waiting"
        
        if files:
            self._show_preview(0)
            self._show_waiting_state()
        
        # Sử dụng storage_dir từ config thay vì output_root mặc định
        if output_root:
            self.output_root = output_root
        else:
            self.output_root = self.storage_dir
        
        logger.info(f"Output directory: {self.output_root}")
        self._start_processing(files, self.output_root)

    def clear_files(self):
        """Xóa tất cả files khỏi danh sách"""
        while self.file_container_layout.count():
            item = self.file_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.file_items.clear()
        self.file_status.clear()
        self.results_cache.clear()
        self.file_md_paths.clear()

    def _show_preview(self, idx: int, processed=False):
        """Hiển thị preview ảnh của file"""
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
        """Xử lý khi click vào dòng file"""
        status = self.file_status.get(idx, "waiting")
        
        if status == "processing":
            # Nếu đang xử lý, hiển thị bước cuối cùng
            self._show_processing_step("extract_info")
            self._show_preview(idx, processed=False)
            
        elif status == "completed" and idx in self.results_cache:
            # Nếu hoàn thành, hiển thị kết quả
            self._show_result_content()
            md, img = self.results_cache[idx]
            html = markdown.markdown(md, extensions=["tables", "fenced_code", "nl2br"])
            self.markdown_preview.setHtml(html)
            self.raw_text_area.setPlainText(md)
            self._show_preview(idx, processed=True)
            
        elif status == "waiting":
            # Nếu đang chờ, hiển thị trạng thái chờ
            self._show_waiting_state()
            self._show_preview(idx, processed=False)
            
        elif status == "failed":
            # Nếu lỗi, hiển thị trạng thái lỗi
            self._show_error_state()
            self._show_preview(idx, processed=False)

    def _on_reload_requested(self, idx: int):
        """Xử lý yêu cầu reload file"""
        # Kiểm tra xem có worker đang chạy không
        if self.worker and self.worker.isRunning():
            logger.warning(f"Cannot reload file {idx}: worker is running")
            return
        
        # Kiểm tra xem file có đang processing không
        if self.file_status.get(idx) == "processing":
            logger.warning(f"Cannot reload file {idx}: file is currently processing")
            return
        
        # Reset trạng thái file về waiting
        self.file_status[idx] = "waiting"
        self.file_items[idx].update_status("waiting")
        
        # Xóa kết quả cũ nếu có
        if idx in self.results_cache:
            del self.results_cache[idx]
        if idx in self.file_md_paths:
            del self.file_md_paths[idx]
        
        # Hiển thị waiting state nếu đang xem file này
        if idx == self.current_preview_index:
            self._show_waiting_state()
            self._show_preview(idx, processed=False)
        
        # Bắt đầu xử lý lại file này
        self._start_processing(self.files, self.output_root, file_indices=[idx])
        
        logger.info(f"Reloading file {idx}: {self.files[idx].name}")

    def _start_processing(self, files, out_root, file_indices: list[int] = None):
        """Bắt đầu xử lý OCR"""
        if self.worker and self.worker.isRunning():
            logger.warning("Worker is already running")
            return
        
        self._show_waiting_state()
        self.worker = OCRWorker(files, out_root, file_indices=file_indices)
        self.worker.progress.connect(self._on_progress)
        self.worker.step_progress.connect(self._on_step_progress)
        self.worker.result.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.finished.connect(self._on_finished)
        self.worker.stopped.connect(self._on_stopped)
        self.stop_btn.setEnabled(True)
        self.back_btn.setEnabled(False)
        self.worker.start()

    def _on_progress(self, idx, status):
        """Cập nhật trạng thái xử lý"""
        self.file_items[idx].update_status(status)
        self.file_status[idx] = status
        if status == "processing":
            self._show_preview(idx, processed=False)

    def _on_step_progress(self, idx, step: str):
        """Xử lý cập nhật từng bước xử lý"""
        # Chỉ hiển thị step nếu đang xem file đang được xử lý
        if idx == self.current_preview_index:
            self._show_processing_step(step)

    def _on_result(self, idx, text, img):
        """Xử lý kết quả OCR"""
        self.results_cache[idx] = (text, img)
        self.file_items[idx].update_status("completed")
        self.file_status[idx] = "completed"
        
        # Lưu đường dẫn file markdown
        img_name = self.files[idx].stem
        md_path = self.output_root / img_name / "text" / f"{img_name}_processed.md"
        self.file_md_paths[idx] = md_path
        
        # Chỉ hiển thị kết quả nếu đang xem file này
        if idx == self.current_preview_index:
            self._show_result_content()
            html = markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br"])
            self.markdown_preview.setHtml(html)
            self.raw_text_area.setPlainText(text)
            self._show_preview(idx, processed=True)
        
        self.save_btn.setEnabled(True)
        self.save_as_btn.setEnabled(True)

    def _on_error(self, idx, msg):
        """Xử lý lỗi OCR"""
        self.file_items[idx].update_status("failed")
        self.file_status[idx] = "failed"
        
        # Chỉ hiển thị error nếu đang xem file này
        if idx == self.current_preview_index:
            self._show_error_state()
        
        logger.error(f"OCR error on file {idx}: {msg}")

    def _on_finished(self):
        """Xử lý khi worker hoàn thành"""
        self.stop_btn.setEnabled(False)
        self.back_btn.setEnabled(True)
        logger.info("OCR worker finished.")
    
    def _on_stopped(self):
        """Xử lý khi worker bị dừng giữa chừng"""
        self.stop_btn.setEnabled(False)
        self.back_btn.setEnabled(True)
        
        # Reset các file đang processing về waiting
        for idx, status in self.file_status.items():
            if status == "processing":
                self.file_status[idx] = "waiting"
                self.file_items[idx].update_status("waiting")
        
        # Hiển thị empty state
        self._show_empty_state()
        logger.info("OCR worker stopped by user.")

    def _stop_ocr(self):
        """Dừng xử lý OCR - Tối ưu không lag"""
        if self.worker and self.worker.isRunning():
            # Disable nút stop ngay lập tức để tránh click nhiều lần
            self.stop_btn.setEnabled(False)
            self.stop_btn.setText("Stopping...")
            
            # Gọi stop worker
            self.worker.stop()
            
            # Sử dụng QTimer để đợi worker dừng mà không block UI
            from PySide6.QtCore import QTimer
            
            timeout_counter = [0]
            
            def check_worker_stopped():
                if not self.worker.isRunning():
                    self.stop_btn.setText("Stop OCR")
                    logger.info("OCR stopped successfully")
                else:
                    timeout_counter[0] += 1
                    if timeout_counter[0] > 20:
                        logger.warning("Force terminating worker...")
                        self.worker.terminate_worker()
                        self.worker.wait(1000)
                        self.stop_btn.setText("Stop OCR")
                        self._on_stopped()
            
            timer = QTimer()
            timer.timeout.connect(check_worker_stopped)
            timer.start(100)
            self._stop_timer = timer    