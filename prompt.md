```bash
ocr_medical                                    
├─ assets                                      
│  ├─ fonts                                    
│  ├─ gif                                      
│  │  └─ loading.gif                           
│  ├─ icon                                     
│  │  ├─ back-page.svg                         
│  │  ├─ camera.svg                            
│  │  ├─ circle.svg                            
│  │  ├─ close.svg                             
│  │  ├─ file.svg                              
│  │  ├─ folder.svg                            
│  │  ├─ folder_plus.svg                       
│  │  ├─ full_screen.svg                       
│  │  ├─ home.svg                              
│  │  ├─ link.svg                              
│  │  ├─ more.svg                              
│  │  ├─ no_image.svg                          
│  │  ├─ review.svg                            
│  │  ├─ save.svg                              
│  │  ├─ scan.svg                              
│  │  ├─ search.svg                            
│  │  ├─ setting.svg                           
│  │  ├─ stop_ocr.svg                          
│  │  ├─ success.svg                           
│  │  ├─ upload.svg                            
│  │  └─ user.svg                              
│  └─ logo                                     
│     ├─ logo-text.png                         
│     └─ logo.png                              
├─ config                                      
│  ├─ app_config.json                          
│  └─ __init__.py                              
├─ core
│  ├─ models                                                  
│  ├─ ocr_extract.py                           
│  ├─ pipeline.py                              
│  ├─ process_image.py                         
│  ├─ status.py                                
│  ├─ waifu2x_loader.py                        
│  └─ __init__.py                              
├─ data                                        
│  ├─ output                                   
│  └─ samples                                                        
├─ ui                                          
│  ├─ pages                                            
│  │  ├─ base_page.py                          
│  │  ├─ extract_info_page.py                  
│  │  ├─ file_log_page.py                      
│  │  ├─ home_page.py                          
│  │  ├─ review_page.py                        
│  │  ├─ setting_page.py                       
│  │  └─ __init__.py                           
│  ├─ style                                    
│  │  ├─ pages                                 
│  │  │  ├─ dialogs.qss.tpl                    
│  │  │  ├─ extract_info_page.qss.tpl          
│  │  │  ├─ file_log_page.qss.tpl              
│  │  │  ├─ home_page.qss.tpl                  
│  │  │  ├─ review_page.qss.tpl                
│  │  │  ├─ setting_page.qss.tpl               
│  │  │  └─ style.qss.tpl                      
│  │  ├─ theme                                 
│  │  │  ├─ theme_dark.json                    
│  │  │  └─ theme_light.json                            
│  │  ├─ style_loader.py                       
│  │  ├─ theme_manager.py                      
│  │  └─ __init__.py                           
│  ├─ widgets                                        
│  │  ├─ dialog_manager.py                     
│  │  ├─ side_panel.py                         
│  │  └─ __init__.py                                       
│  ├─ main_window.py                           
│  └─ __init__.py                              
├─ utils                                       
│  ├─ helpers.py                               
│  ├─ logger.py                                
│  └─ __init__.py                                             
├─ main.py                                     
├─ requirements.txt                            
├─ watch.py                                    
└─ __init__.py                                 
```

# 📜 Code chi tiết

## `base_page.py`
**Path:** `ocr_medical/ui/pages/base_page.py`

```python
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from ocr_medical.ui.style.style_loader import load_theme_qss
from ocr_medical.ui.style.theme_manager import ThemeManager


# Map tên class của page với tên file QSS tương ứng
PAGE_QSS_MAP = {
    "HomePage": "home_page",
    "ExtraInfoPage": "extract_info_page",
    "FileLogPage": "file_log_page",
    "ReviewPage": "review_page",
    "SettingPage": "setting_page",
}


class BasePage(QWidget):
    """
    Class cơ sở cho tất cả các trang trong ứng dụng.
    Cung cấp cấu trúc chung: header, divider và hỗ trợ theme động.
    """
    def __init__(self, title: str, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__(parent)
        self.theme_manager = theme_manager
        
        # Đặt object name để dễ dàng styling bằng QSS
        self.setObjectName(f"Page__{title.replace(' ', '_')}")

        # Tạo layout chính với margin và spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- Header: Tiêu đề trang ---
        self.header = QLabel(title)
        self.header.setObjectName("PageHeader")
        layout.addWidget(self.header)

        # --- Divider: Đường phân cách ngang ---
        self.divider = QFrame()
        self.divider.setObjectName("Divider")
        self.divider.setFrameShape(QFrame.HLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(self.divider)

        # Lắng nghe sự kiện đổi theme để cập nhật giao diện
        self.theme_manager.theme_changed.connect(self.apply_theme)

        # Áp dụng theme ban đầu
        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name(),
        )

    def apply_theme(self, theme_data: dict, theme_name: str):
        """
        Áp dụng theme cho page.
        Tự động load file QSS tương ứng dựa vào tên class.
        """
        class_name = self.__class__.__name__
        page_name = PAGE_QSS_MAP.get(class_name, None)

        if page_name:
            try:
                # Load file QSS từ theme hiện tại
                qss = load_theme_qss(theme_name, page_name)
                self.setStyleSheet(qss)
            except FileNotFoundError:
                # Nếu không tìm thấy file QSS, xóa stylesheet
                self.setStyleSheet("")
```

## `extract_info_page.py`
**Path:** `ocr_medical/ui/pages/extract_info_page.py`

```python
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
import sys

logger = logging.getLogger(__name__)


# =====================================================
#             OCR Worker Thread
# =====================================================
class OCRWorker(QThread):
    """Worker thread để xử lý OCR không block UI"""

    progress = Signal(int, str)  # (index, status)
    # (index, step: "load_model", "process_image", "extract_info", "success")
    step_progress = Signal(int, str)
    result = Signal(int, str, str)  # (index, markdown_text, image_path)
    finished = Signal()
    error = Signal(int, str)
    stopped = Signal()  # Signal khi bị dừng

    def __init__(self, files: list[Path], output_root: Path, page_instance=None, file_indices: list[int] = None):
        super().__init__()
        self.files = files
        self.output_root = output_root
        self.page_instance = page_instance
        self.file_indices = file_indices
        self._is_running = True
        self._force_stop = False

    def run(self):
        from ocr_medical.core.waifu2x_loader import load_waifu2x
        from ocr_medical.core.process_image import process_image
        from ocr_medical.core.ocr_extract import call_qwen_ocr
        from PIL import Image

        try:
            # Xác định danh sách file cần xử lý
            if self.file_indices:
                files_to_process = [(idx, self.files[idx])
                                    for idx in self.file_indices]
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
                    logger.info(
                        f"Processing file {idx + 1}/{len(self.files)}: {file_path.name}")

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
                    _, processed_path = process_image(
                        upscaler, img, img_name, self.output_root)

                    if not self._is_running:
                        self.stopped.emit()
                        return

                    # Bước 3: Extract information (OCR)
                    self.step_progress.emit(idx, "extract_info")
                    from ocr_medical.core.pipeline import DEFAULT_PROMPT
                    out_dir_text = self.output_root / img_name / "text"
                    out_dir_text.mkdir(parents=True, exist_ok=True)

                    extracted = call_qwen_ocr(
                        str(processed_path), DEFAULT_PROMPT)

                    if not self._is_running:
                        self.stopped.emit()
                        return

                    md_path = out_dir_text / f"{img_name}_processed.md"
                    with open(md_path, "w", encoding="utf-8") as f:
                        f.write(extracted)

                    markdown_text = extracted
                    processed_img = self.output_root / img_name / \
                        "processed" / f"{img_name}_processed.png"

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

        self.reload_btn.clicked.connect(
            lambda: self.reload_requested.emit(self.index))
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
        self.preview_box.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        no_img = self.project_root / "assets" / "icon" / "no_image.svg"
        if no_img.exists():
            icon = load_svg_colored(
                no_img, self.theme_data["color"]["text"]["muted"], 100)
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
        self.empty_state_tab1 = QLabel(
            "No content yet. Start processing to see results.")
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
        self.processing_text_tab1.setStyleSheet(
            "font-size: 16px; font-weight: 500;")
        processing_layout_tab1.addWidget(self.processing_text_tab1)

        processing_layout_main_tab1.addWidget(
            self.processing_container_tab1, alignment=Qt.AlignCenter)
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
        self.empty_state_tab2 = QLabel(
            "No content yet. Start processing to see results.")
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
        self.processing_text_tab2.setStyleSheet(
            "font-size: 16px; font-weight: 500;")
        processing_layout_tab2.addWidget(self.processing_text_tab2)

        processing_layout_main_tab2.addWidget(
            self.processing_container_tab2, alignment=Qt.AlignCenter)
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
        self.back_btn.clicked.connect(
            lambda: self.navigate_back_requested.emit())
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
                            logger.info(
                                f"Using custom storage path: {custom_dir}")
                            return custom_dir
                        else:
                            logger.warning(
                                f"Storage_path không tồn tại: {custom_dir}")

            # Nếu không có config hoặc storage_dir rỗng, dùng AppData mặc định
            from PySide6.QtCore import QStandardPaths
            app_data = QStandardPaths.writableLocation(
                QStandardPaths.AppDataLocation)
            default_path = Path(app_data) / "OCR-Medical" / "output"
            default_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using default AppData directory: {default_path}")
            return default_path

        except Exception as e:
            logger.error(
                f"Error loading storage directory from config: {str(e)}")
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
            completed_count = sum(
                1 for status in self.file_status.values() if status == "completed")
            total_count = len(self.files)
            self.processing_text_tab1.setText(
                f"Success! Extracted {completed_count}/{total_count} file(s)")
            self.processing_text_tab2.setText(
                f"Success! Extracted {completed_count}/{total_count} file(s)")

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
            self.raw_text_area.textChanged.disconnect(
                self._update_live_preview)
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
        html = markdown.markdown(
            text, extensions=["tables", "fenced_code", "nl2br"])
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
        default_dir = str(self.storage_dir) if self.storage_dir else str(
            self.output_root)

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
                scaled = pix.scaled(self.preview_box.size(),
                                    Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
            html = markdown.markdown(
                md, extensions=["tables", "fenced_code", "nl2br"])
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
            logger.warning(
                f"Cannot reload file {idx}: file is currently processing")
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
        self._start_processing(
            self.files, self.output_root, file_indices=[idx])

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
        md_path = self.output_root / img_name / \
            "text" / f"{img_name}_processed.md"
        self.file_md_paths[idx] = md_path

        # Chỉ hiển thị kết quả nếu đang xem file này
        if idx == self.current_preview_index:
            self._show_result_content()
            html = markdown.markdown(
                text, extensions=["tables", "fenced_code", "nl2br"])
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

```

## `file_log_page.py`
**Path:** `ocr_medical/ui/pages/file_log_page.py`

```python
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox,
    QFrame, QDialog, QTextEdit, QComboBox, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, QSize, QStandardPaths
from PySide6.QtGui import QPixmap, QPainter, QMouseEvent
from pathlib import Path
import json
from datetime import datetime
import shutil
import logging

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager

logger = logging.getLogger(__name__)
ITEMS_PER_PAGE = 6


# =====================================================
# Image Compare Widget
# =====================================================
class ImageCompareWidget(QFrame):
    """So sánh ảnh original / processed bằng thanh kéo"""
    def __init__(self, original: Path, processed: Path):
        super().__init__()
        self.original = QPixmap(str(original)) if original and original.exists() else None
        self.processed = QPixmap(str(processed)) if processed and processed.exists() else None
        self.slider_pos = 0.5
        self.setMinimumHeight(500)
        self.setMouseTracking(True)
        self.setObjectName("ImageCompare")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        
        if not (self.original and self.processed):
            painter.setPen(Qt.gray)
            painter.drawText(self.rect(), Qt.AlignCenter, "(Missing image files)")
            return

        size = self.size()
        
        # Scale images to fit while maintaining aspect ratio
        ori_scaled = self.original.scaled(
            size, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        proc_scaled = self.processed.scaled(
            size, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        # Center images
        ori_x = (size.width() - ori_scaled.width()) // 2
        ori_y = (size.height() - ori_scaled.height()) // 2
        proc_x = (size.width() - proc_scaled.width()) // 2
        proc_y = (size.height() - proc_scaled.height()) // 2
        
        split_x = int(size.width() * self.slider_pos)
        
        # Draw original image (left side)
        painter.setClipRect(0, 0, split_x, size.height())
        painter.drawPixmap(ori_x, ori_y, ori_scaled)
        
        # Draw processed image (right side)
        painter.setClipRect(split_x, 0, size.width() - split_x, size.height())
        painter.drawPixmap(proc_x, proc_y, proc_scaled)
        
        # Draw slider line
        painter.setClipping(False)
        painter.setPen(Qt.black)
        painter.drawLine(split_x, 0, split_x, size.height())

    def mouseMoveEvent(self, event: QMouseEvent):
        self.slider_pos = max(0.0, min(1.0, event.position().x() / self.width()))
        self.update()


# =====================================================
# Detail Dialog
# =====================================================
class FileDetailDialog(QDialog):
    """Hiển thị ảnh và markdown song song với khả năng scroll"""
    def __init__(self, folder: Path, theme_data: dict, parent=None):
        super().__init__(parent)
        self.folder = folder
        self.theme_data = theme_data
        self.setWindowTitle(f"Details - {folder.name}")
        self.resize(1200, 700)
        self.setObjectName("FileDetailDialog")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Left Panel - Image Compare
        left = QFrame()
        left.setObjectName("LeftPanel")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        lbl = QLabel("🖼️ Compare (Original ↔ Processed)")
        lbl.setStyleSheet("font-weight: 700; font-size: 15px;")
        left_layout.addWidget(lbl)

        # Find images
        ori = None
        proc = None
        
        original_dir = folder / "original"
        processed_dir = folder / "processed"
        
        if original_dir.exists():
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']:
                files = list(original_dir.glob(ext))
                if files:
                    ori = files[0]
                    break
        
        if processed_dir.exists():
            for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif']:
                files = list(processed_dir.glob(ext))
                if files:
                    proc = files[0]
                    break

        # Image info
        info_text = ""
        if ori and ori.exists():
            pixmap = QPixmap(str(ori))
            size_mb = ori.stat().st_size / (1024 * 1024)
            info_text = f"Original: {pixmap.width()}x{pixmap.height()}px, {size_mb:.2f}MB"
        
        if proc and proc.exists():
            pixmap = QPixmap(str(proc))
            size_mb = proc.stat().st_size / (1024 * 1024)
            if info_text:
                info_text += " | "
            info_text += f"Processed: {pixmap.width()}x{pixmap.height()}px, {size_mb:.2f}MB"
        
        if info_text:
            info_label = QLabel(info_text)
            info_label.setStyleSheet("color: #666; font-size: 12px;")
            left_layout.addWidget(info_label)

        # Scroll area for image
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        self.img_cmp = ImageCompareWidget(ori, proc)
        scroll.setWidget(self.img_cmp)
        left_layout.addWidget(scroll, 1)

        # Right Panel - Markdown Editor
        right = QFrame()
        right.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        title = QLabel("📝 Extracted Markdown (Editable)")
        title.setStyleSheet("font-weight: 700; font-size: 15px;")
        right_layout.addWidget(title)

        self.editor = QTextEdit()
        self.editor.setObjectName("MarkdownEditor")
        self.editor.setAcceptRichText(False)
        self.editor.setStyleSheet("font-size: 14px; font-family: 'Consolas', 'Monaco', monospace;")
        right_layout.addWidget(self.editor, 1)

        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._save)
        right_layout.addWidget(self.save_btn, alignment=Qt.AlignRight)

        # Load markdown
        self.text_path = None
        text_dir = folder / "text"
        if text_dir.exists():
            md_files = list(text_dir.glob("*.md"))
            if md_files:
                self.text_path = md_files[0]
                if self.text_path.exists():
                    try:
                        content = self.text_path.read_text(encoding="utf-8")
                        self.editor.setPlainText(content)
                    except Exception as e:
                        logger.error(f"Error reading markdown: {e}")
                        self.editor.setPlainText(f"Error loading file: {e}")

        main_layout.addWidget(left, 5)
        main_layout.addWidget(right, 5)

    def _save(self):
        if not self.text_path:
            QMessageBox.warning(self, "Error", "Markdown file not found.")
            return
        
        try:
            self.text_path.write_text(self.editor.toPlainText(), encoding="utf-8")
            QMessageBox.information(self, "Saved", "File saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file: {e}")


# =====================================================
# Folder Card
# =====================================================
class FolderCard(QFrame):
    def __init__(self, folder: Path, theme_data: dict, project_root: Path, view_cb, del_cb):
        super().__init__()
        self.folder = folder
        self.view_cb = view_cb
        self.del_cb = del_cb
        self.setObjectName("FolderCard")
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header
        head = QHBoxLayout()
        head.setSpacing(8)
        
        name = QLabel(folder.name)
        name.setObjectName("FolderName")
        name.setWordWrap(True)
        head.addWidget(name, 1)
        
        status, color = self._get_status()
        badge = QLabel(status)
        badge.setObjectName("StatusBadge")
        badge.setStyleSheet(f"background:{color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;")
        head.addWidget(badge)
        layout.addLayout(head)

        # Info
        info = QHBoxLayout()
        info.setSpacing(12)
        info.addWidget(QLabel(f"📄 Files: {self._count()}"))
        info.addWidget(QLabel(f"🕒 {self._time()}"))
        info.addWidget(QLabel(f"📦 {self._size()}"))
        info.addStretch()
        layout.addLayout(info)

        # Actions
        btns = QHBoxLayout()
        btns.setSpacing(8)
        btns.addStretch()
        
        view = QPushButton("View Details")
        view.setObjectName("ViewBtn")
        view.setCursor(Qt.PointingHandCursor)
        view.clicked.connect(lambda: view_cb(folder))
        
        delete = QPushButton("Delete")
        delete.setObjectName("DeleteBtn")
        delete.setCursor(Qt.PointingHandCursor)
        delete.clicked.connect(lambda: del_cb(folder))
        
        btns.addWidget(view)
        btns.addWidget(delete)
        layout.addLayout(btns)

    def _get_status(self):
        text_dir = self.folder / "text"
        proc_dir = self.folder / "processed"
        orig_dir = self.folder / "original"
        
        has_text = text_dir.exists() and any(text_dir.iterdir())
        has_proc = proc_dir.exists() and any(proc_dir.iterdir())
        has_orig = orig_dir.exists() and any(orig_dir.iterdir())
        
        if has_text and has_proc and has_orig:
            return "Success", "#22C55E"
        elif has_proc:
            return "Partial", "#FB923C"
        return "Pending", "#3B82F6"

    def _count(self):
        try:
            return sum(1 for _ in self.folder.rglob("*") if _.is_file())
        except Exception:
            return 0

    def _size(self):
        try:
            total_size = sum(f.stat().st_size for f in self.folder.rglob("*") if f.is_file())
            return f"{total_size / (1024*1024):.2f} MB"
        except Exception:
            return "0.00 MB"

    def _time(self):
        try:
            mtime = datetime.fromtimestamp(self.folder.stat().st_mtime)
            return mtime.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return "Unknown"


# =====================================================
# FileLogPage
# =====================================================
class FileLogPage(BasePage):
    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__("File Log", theme_manager, parent)
        layout = self.layout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.output_dir = self._load_storage()
        self.theme_data = theme_manager.get_theme_data()
        self.all_folders = []
        self.filtered = []
        self.current_page = 1
        self.search_text = ""

        # === Top Bar ===
        top = QHBoxLayout()
        top.setSpacing(8)

        self.search = QLineEdit()
        self.search.setObjectName("SearchBar")
        self.search.setPlaceholderText("Search folders...")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._on_search_changed)
        top.addWidget(self.search, 3)

        self.sort = QComboBox()
        self.sort.setObjectName("SortBox")
        self.sort.addItems(["Date (Newest)", "Date (Oldest)", "Name (A-Z)", "Name (Z-A)", "Size (Largest)", "Size (Smallest)"])
        self.sort.currentTextChanged.connect(self._on_sort_changed)
        self.sort.setCursor(Qt.PointingHandCursor)
        top.addWidget(self.sort, 1)

        self.refresh = QPushButton("Refresh")
        self.refresh.setObjectName("RefreshBtn")
        self.refresh.setCursor(Qt.PointingHandCursor)
        self.refresh.clicked.connect(self.load_logs)
        top.addWidget(self.refresh)
        
        layout.addLayout(top)

        # === Summary ===
        self.summary_label = QLabel()
        self.summary_label.setObjectName("SummaryLabel")
        self.summary_label.setStyleSheet("color: #666; font-size: 13px; padding: 4px 0;")
        layout.addWidget(self.summary_label)

        # === Cards Container ===
        self.card_container = QWidget()
        self.card_layout = QVBoxLayout(self.card_container)
        self.card_layout.setSpacing(10)
        self.card_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.card_container, 1)

        # === Pagination ===
        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        self.page_info_label = QLabel()
        self.page_info_label.setObjectName("PageInfo")
        self.page_info_label.setStyleSheet("font-size: 13px; color: #666;")
        bottom.addWidget(self.page_info_label)

        bottom.addStretch()
        
        self.prev = QPushButton("◀ Previous")
        self.prev.setObjectName("PageBtn")
        self.prev.setCursor(Qt.PointingHandCursor)
        self.prev.clicked.connect(self._prev_page)
        bottom.addWidget(self.prev)

        self.page_label = QLabel()
        self.page_label.setObjectName("PageLbl")
        self.page_label.setStyleSheet("font-weight: 600; font-size: 14px; padding: 0 12px;")
        bottom.addWidget(self.page_label)

        self.next = QPushButton("Next ▶")
        self.next.setObjectName("PageBtn")
        self.next.setCursor(Qt.PointingHandCursor)
        self.next.clicked.connect(self._next_page)
        bottom.addWidget(self.next)
        
        layout.addLayout(bottom)

        # Load initial data
        self.load_logs()

    def _load_storage(self):
        """Load storage directory từ config file (ưu tiên storage_path nếu có, ngược lại dùng AppData)"""
        from PySide6.QtCore import QStandardPaths
        cfg = self.project_root / "config" / "app_config.json"
        try:
            if cfg.exists():
                with cfg.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    storage_path_str = data.get("storage_path", "").strip()
                    if storage_path_str:
                        custom_dir = Path(storage_path_str)
                        if custom_dir.exists():
                            logger.info(f"📁 Using custom storage path: {custom_dir}")
                            return custom_dir
                        else:
                            logger.warning(f"⚠️ storage_path không tồn tại: {custom_dir}")
            # fallback AppData
            default = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / "OCR-Medical" / "output"
            default.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using default AppData directory: {default}")
            return default
        except Exception as e:
            logger.error(f"Error loading storage path: {e}")
            fallback = Path.cwd() / "data" / "output"
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback

    def load_logs(self):
        """Load all folders from output directory"""
        try:
            self.all_folders = [f for f in self.output_dir.iterdir() if f.is_dir()]
            self._apply_filters()
        except Exception as e:
            logger.error(f"Error loading logs: {e}")
            self.all_folders = []
            self.filtered = []
            self._update_page()

    def _on_search_changed(self, text: str):
        """Handle search text change"""
        self.search_text = text.lower().strip()
        self.current_page = 1
        self._apply_filters()

    def _on_sort_changed(self):
        """Handle sort option change"""
        self._apply_filters()

    def _apply_filters(self):
        """Apply search and sort filters"""
        # Apply search filter
        if self.search_text:
            self.filtered = [f for f in self.all_folders if self.search_text in f.name.lower()]
        else:
            self.filtered = self.all_folders.copy()
        
        # Apply sort
        mode = self.sort.currentText()
        try:
            if "Date" in mode:
                reverse = "Newest" in mode
                self.filtered.sort(key=lambda f: f.stat().st_mtime, reverse=reverse)
            elif "Name" in mode:
                reverse = "Z-A" in mode
                self.filtered.sort(key=lambda f: f.name.lower(), reverse=reverse)
            elif "Size" in mode:
                reverse = "Largest" in mode
                self.filtered.sort(
                    key=lambda f: sum(x.stat().st_size for x in f.rglob("*") if x.is_file()), 
                    reverse=reverse
                )
        except Exception as e:
            logger.error(f"Error sorting: {e}")
        
        self._update_page()

    def _update_page(self):
        """Update the current page display"""
        # Clear existing cards
        for i in reversed(range(self.card_layout.count())):
            widget = self.card_layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()

        total_items = len(self.filtered)
        total_pages = max(1, (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        self.current_page = max(1, min(self.current_page, total_pages))
        
        start_idx = (self.current_page - 1) * ITEMS_PER_PAGE
        end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)

        # Add cards for current page
        if total_items > 0:
            for folder in self.filtered[start_idx:end_idx]:
                card = FolderCard(folder, self.theme_data, self.project_root, self._view_details, self._delete_folder)
                self.card_layout.addWidget(card)
        else:
            # Show empty state
            empty_label = QLabel("No folders found")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #999; font-size: 16px; padding: 40px;")
            self.card_layout.addWidget(empty_label)

        # Add stretch at the end
        self.card_layout.addStretch()

        # Update labels
        if total_items > 0:
            self.page_label.setText(f"Page {self.current_page} of {total_pages}")
            self.page_info_label.setText(f"Showing {start_idx + 1}-{end_idx} of {total_items} folders")
            
            total_size = sum(
                sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
                for folder in self.filtered
            )
            self.summary_label.setText(
                f"Total: {total_items} folders | {total_size / (1024*1024):.2f} MB"
            )
        else:
            self.page_label.setText("Page 0 of 0")
            self.page_info_label.setText("No folders to display")
            self.summary_label.setText("Total: 0 folders | 0.00 MB")

        # Update button states
        self.prev.setEnabled(self.current_page > 1)
        self.next.setEnabled(self.current_page < total_pages)

    def _prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_page()

    def _next_page(self):
        """Go to next page"""
        total_pages = max(1, (len(self.filtered) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        if self.current_page < total_pages:
            self.current_page += 1
            self._update_page()

    def _view_details(self, folder: Path):
        """Open detail dialog for folder"""
        try:
            dialog = FileDetailDialog(folder, self.theme_data, self)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error opening details: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open details: {e}")

    def _delete_folder(self, folder: Path):
        """Delete folder with confirmation"""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete '{folder.name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                shutil.rmtree(folder, ignore_errors=True)
                QMessageBox.information(self, "Deleted", f"Folder '{folder.name}' has been deleted.")
                self.load_logs()
            except Exception as e:
                logger.error(f"Error deleting folder: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete folder: {e}")
```

## `home_page.py`
**Path:** `ocr_medical/ui/pages/home_page.py`

```python
from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QSize, QStandardPaths
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLineEdit, QSizePolicy,
                               QPushButton, QLabel, QFrame, QFileDialog, QWidget,
                               QScrollArea, QMessageBox, QGridLayout)
from PySide6.QtGui import QAction
from threading import Lock
import os
import logging
import json

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored
from ocr_medical.ui.widgets.dialog_manager import DialogManager

# ============= CONSTANTS =============
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}
ICON_SIZE_SMALL = 16
ICON_SIZE_MEDIUM = 18
ICON_SIZE_LARGE = 48

# Setup logger
logger = logging.getLogger(__name__)


class FileItem(QFrame):
    """
    Widget hiển thị thông tin của 1 file trong danh sách.
    Bao gồm: index, icon, tên file, kích thước, nút xóa.
    """
    def __init__(self, index: int, file_path: Path, theme_data: dict, project_root: Path,
                 remove_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("FileItem")

        self.file_path = Path(file_path)
        self.remove_callback = remove_callback
        self.theme_data = theme_data
        self.project_root = project_root

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(0)

        # ======= Column 1: Index (Proportion 1) =======
        index_container = QFrame()
        index_container.setObjectName("FileItemColumn")
        index_layout = QHBoxLayout(index_container)
        index_layout.setContentsMargins(12, 0, 12, 0)
        index_layout.setSpacing(0)
        
        index_label = QLabel(str(index))
        index_label.setObjectName("FileIndex")
        index_label.setAlignment(Qt.AlignCenter)
        index_layout.addWidget(index_label)
        layout.addWidget(index_container, 1)
        
        # ======= Column 2: Icon + File Name (Proportion 4) =======
        name_container = QFrame()
        name_container.setObjectName("FileItemColumn")
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(12, 0, 12, 0)
        name_layout.setSpacing(8)

        file_icon_path = project_root / "assets" / "icon" / "file.svg"
        icon_label = QLabel()
        try:
            if file_icon_path.exists():
                icon = load_svg_colored(file_icon_path, "#1A73E8", ICON_SIZE_MEDIUM)
                icon_label.setPixmap(icon.pixmap(QSize(ICON_SIZE_MEDIUM, ICON_SIZE_MEDIUM)))
        except Exception as e:
            logger.warning(f"Failed to load file icon: {e}")
        
        icon_label.setFixedSize(25, 25)
        icon_label.setObjectName("FileIcon")
        name_layout.addWidget(icon_label)

        self.name_label = QLabel(self.file_path.name)
        self.name_label.setObjectName("FileName")
        name_layout.addWidget(self.name_label, 1)
        layout.addWidget(name_container, 4)

        # ======= Column 3: Size (Proportion 4) =======
        size_container = QFrame()
        size_container.setObjectName("FileItemColumn")
        size_layout = QHBoxLayout(size_container)
        size_layout.setContentsMargins(12, 0, 12, 0)
        size_layout.setSpacing(0)

        try:
            size_kb = os.path.getsize(self.file_path) / 1024
            size_txt = f"{size_kb/1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
        except Exception as e:
            logger.warning(f"Failed to get file size for {self.file_path.name}: {e}")
            size_txt = "--"
        
        size_label = QLabel(size_txt)
        size_label.setObjectName("FileSize")
        size_layout.addWidget(size_label)
        layout.addWidget(size_container, 4)

        # ======= Column 4: Action (Proportion 1) =======
        action_container = QFrame()
        action_container.setObjectName("FileItemColumn")
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(12, 0, 12, 0)
        action_layout.setSpacing(0)

        close_icon_path = project_root / "assets" / "icon" / "close.svg"
        delete_btn = QPushButton()
        delete_btn.setObjectName("DeleteButton")
        try:
            if close_icon_path.exists():
                delete_btn.setIcon(load_svg_colored(close_icon_path, "#666", ICON_SIZE_MEDIUM))
        except Exception as e:
            logger.warning(f"Failed to load close icon: {e}")
        
        delete_btn.setFixedSize(28, 28)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.remove_self)
        action_layout.addWidget(delete_btn, alignment=Qt.AlignCenter)
        layout.addWidget(action_container, 1)

    def remove_self(self):
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Remove "{self.file_path.name}" from the list?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.setParent(None)
            self.deleteLater()
            self.remove_callback(self.file_path)


class DropArea(QFrame):
    """
    Khung upload hỗ trợ click và drag & drop với visual feedback
    """
    def __init__(self, on_files_selected, parent=None):
        super().__init__(parent)
        self.on_files_selected = on_files_selected
        self.setAcceptDrops(True)
        self.setObjectName("UploadBox")
        self._dragging = False

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            dlg = QFileDialog(self, "Select files")
            dlg.setFileMode(QFileDialog.ExistingFiles)
            dlg.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff)")
            if dlg.exec():
                paths = [Path(p) for p in dlg.selectedFiles()]
                self.on_files_selected(paths)
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self._dragging = True
            self.setObjectName("UploadBox_Dragging")
            self.style().unpolish(self)
            self.style().polish(self)
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._dragging = False
        self.setObjectName("UploadBox")
        self.style().unpolish(self)
        self.style().polish(self)
        event.accept()

    def dropEvent(self, event):
        self._dragging = False
        self.setObjectName("UploadBox")
        self.style().unpolish(self)
        self.style().polish(self)

        urls = event.mimeData().urls()
        paths = [Path(u.toLocalFile()) for u in urls if u.isLocalFile()]
        if paths:
            self.on_files_selected(paths)
        event.acceptProposedAction()


class FileListHeader(QFrame):
    """
    Header row cho danh sách file (giống Excel với proportional columns)
    """
    def __init__(self, theme_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("FileListHeader")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(0)

        # ======= Column 1: # (Proportion 1) =======
        index_container = QFrame()
        index_container.setObjectName("FileHeaderColumn")
        index_layout = QHBoxLayout(index_container)
        index_layout.setContentsMargins(12, 0, 12, 0)
        index_layout.setSpacing(0)
        
        index_header = QLabel("#")
        index_header.setObjectName("FileHeaderLabel")
        index_header.setAlignment(Qt.AlignCenter)
        index_layout.addWidget(index_header)
        layout.addWidget(index_container, 1)

        # ======= Column 2: File Name (Proportion 4) =======
        name_container = QFrame()
        name_container.setObjectName("FileHeaderColumn")
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(12, 0, 12, 0)
        name_layout.setSpacing(0)
        
        name_header = QLabel("File Name")
        name_header.setObjectName("FileHeaderLabel")
        name_layout.addWidget(name_header)
        layout.addWidget(name_container, 4)

        # ======= Column 3: Size (Proportion 4) =======
        size_container = QFrame()
        size_container.setObjectName("FileHeaderColumn")
        size_layout = QHBoxLayout(size_container)
        size_layout.setContentsMargins(12, 0, 12, 0)
        size_layout.setSpacing(0)
        
        size_header = QLabel("Size")
        size_header.setObjectName("FileHeaderLabel")
        size_layout.addWidget(size_header)
        layout.addWidget(size_container, 4)

        # ======= Column 4: Action (Proportion 1) =======
        action_container = QFrame()
        action_container.setObjectName("FileHeaderColumn")
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(12, 0, 12, 0)
        action_layout.setSpacing(0)
        
        action_header = QLabel("")
        action_header.setObjectName("FileHeaderLabel")
        action_layout.addWidget(action_header, alignment=Qt.AlignCenter)
        layout.addWidget(action_container, 1)


class HomePage(BasePage):
    """
    Trang chủ - nơi người dùng upload và quản lý file đầu vào
    """
    process_requested = Signal(list)

    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("OCR - Medical", theme_manager, parent)

        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.theme_data = theme_manager.get_theme_data()
        self.files: list[Path] = []
        self.files_set: set = set()  # ✅ Dùng set để kiểm tra O(1)
        self._files_lock = Lock()

        layout = self.layout()

        # ============= HEADER =============
        header_layout = QHBoxLayout()
        layout.removeWidget(self.header)
        header_layout.addWidget(self.header)
        layout.insertLayout(0, header_layout)

        # ============= ACTION BUTTONS =============
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        actions = [
            ("Scan from Folder", "folder_plus.svg", self.scan_from_folder),
            ("Capture with Camera", "camera.svg", self._show_coming_soon_camera),
            ("Fetch from URL", "link.svg", self._show_coming_soon_url),
        ]

        for text, icon_file, handler in actions:
            btn = QPushButton("  " + text)
            btn.setObjectName("ActionButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFocusPolicy(Qt.NoFocus)

            icon_path = self._get_icon_path(icon_file)
            try:
                if icon_path.exists():
                    btn.setIcon(load_svg_colored(icon_path, self.theme_data["color"]["text"]["primary"], ICON_SIZE_MEDIUM))
                    btn.setIconSize(QSize(ICON_SIZE_MEDIUM, ICON_SIZE_MEDIUM))
            except Exception as e:
                logger.warning(f"Failed to load icon {icon_file}: {e}")

            btn.clicked.connect(handler)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        # ============= UPLOAD BOX =============
        upload_box = DropArea(on_files_selected=self.add_files)
        upload_layout = QVBoxLayout(upload_box)
        upload_layout.setContentsMargins(20, 20, 20, 20)
        upload_layout.setSpacing(8)
        upload_layout.setAlignment(Qt.AlignCenter)

        upload_icon_path = self._get_icon_path("upload.svg")
        try:
            if upload_icon_path.exists():
                upload_icon = load_svg_colored(upload_icon_path, self.theme_data["color"]["text"]["primary"], ICON_SIZE_LARGE)
                icon_label = QLabel()
                icon_label.setPixmap(upload_icon.pixmap(QSize(ICON_SIZE_LARGE, ICON_SIZE_LARGE)))
                icon_label.setAlignment(Qt.AlignCenter)
                upload_layout.addWidget(icon_label)
        except Exception as e:
            logger.warning(f"Failed to load upload icon: {e}")

        upload_text = QLabel("Click or drag your files here to extract information")
        upload_text.setObjectName("UploadText")
        upload_text.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_text)

        layout.addWidget(upload_box)

        # ============= STORAGE FRAME =============
        storage_frame = QFrame()
        storage_frame.setObjectName("StorageFrame")
        storage_layout = QHBoxLayout(storage_frame)
        storage_layout.setContentsMargins(0, 0, 0, 0)
        storage_layout.setSpacing(8)

        folder_icon_path = self._get_icon_path("folder.svg")
        folder_box = QFrame()
        folder_box.setObjectName("FolderBox")
        folder_layout = QHBoxLayout(folder_box)
        folder_layout.setContentsMargins(8, 4, 8, 4)
        folder_layout.setSpacing(6)

        try:
            if folder_icon_path.exists():
                folder_icon = load_svg_colored(folder_icon_path, self.theme_data["color"]["text"]["primary"], ICON_SIZE_SMALL)
                folder_icon_label = QLabel()
                folder_icon_label.setPixmap(folder_icon.pixmap(QSize(ICON_SIZE_SMALL, ICON_SIZE_SMALL)))
                folder_layout.addWidget(folder_icon_label)
        except Exception as e:
            logger.warning(f"Failed to load folder icon: {e}")

        folder_label = QLabel("Storage Directory")
        folder_label.setObjectName("StorageLabel")
        folder_layout.addWidget(folder_label)
        storage_layout.addWidget(folder_box)

        # Load storage directory từ config
        default_output = self._load_storage_dir()

        self.storage_path = QLineEdit(str(default_output))
        self.storage_path.setObjectName("StoragePath")
        self.storage_path.setReadOnly(True)
        storage_layout.addWidget(self.storage_path, stretch=1)

        more_icon_path = self._get_icon_path("more.svg")
        self.more_btn = QPushButton()
        self.more_btn.setObjectName("MoreButton")
        self.more_btn.setCursor(Qt.PointingHandCursor)
        self.more_btn.setFixedSize(32, 32)
        try:
            if more_icon_path.exists():
                self.more_btn.setIcon(load_svg_colored(more_icon_path, self.theme_data["color"]["text"]["primary"], ICON_SIZE_SMALL))
                self.more_btn.setIconSize(QSize(ICON_SIZE_SMALL, ICON_SIZE_SMALL))
        except Exception as e:
            logger.warning(f"Failed to load more icon: {e}")
        
        self.more_btn.clicked.connect(self.choose_storage_dir)
        storage_layout.addWidget(self.more_btn)

        layout.addWidget(storage_frame)

        # ============= FILE LIST =============
        self.file_scroll = QScrollArea()
        self.file_scroll.setObjectName("FileList")
        self.file_scroll.setWidgetResizable(True)

        self.file_list_container = QWidget()
        self.file_list_container.setObjectName("FileListContainer")
        self.file_list_layout = QVBoxLayout(self.file_list_container)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_layout.setSpacing(0)

        # Add header row
        file_header = FileListHeader(self.theme_data, self)
        self.file_list_layout.addWidget(file_header)

        # Add separator line
        separator = QFrame()
        separator.setObjectName("FileListSeparator")
        separator.setFixedHeight(1)
        self.file_list_layout.addWidget(separator)

        self.file_list_layout.addSpacing(0)
        self.file_list_layout.setAlignment(Qt.AlignTop)

        self.file_scroll.setWidget(self.file_list_container)
        layout.addWidget(self.file_scroll)

        # ============= FOOTER =============
        footer_layout = QHBoxLayout()

        self.total_files_label = QLabel("Total files: 0")
        self.total_files_label.setObjectName("TotalFilesLabel")
        footer_layout.addWidget(self.total_files_label)

        self.process_btn = QPushButton("Process Document")
        self.process_btn.setObjectName("ProcessButton")
        self.process_btn.setCursor(Qt.PointingHandCursor)
        self.process_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.process_btn.setMinimumHeight(36)
        self.process_btn.setEnabled(False)
        footer_layout.addWidget(self.process_btn, stretch=1)

        self.process_btn.clicked.connect(self._process_files)
        layout.addLayout(footer_layout)

    # ============= HELPER METHODS =============
    def _get_icon_path(self, icon_name: str) -> Path:
        """Helper method to get icon path"""
        return self.project_root / "assets" / "icon" / icon_name

    def _load_storage_dir(self) -> Path:
        """Load storage directory từ config file (ưu tiên storage_path nếu có, rỗng thì dùng AppLocal)"""
        from PySide6.QtCore import QStandardPaths
        import json, logging
        from pathlib import Path
        logger = logging.getLogger(__name__)

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

            app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            default_path = Path(app_data) / "OCR-Medical" / "output"
            default_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using default AppData directory: {default_path}")
            return default_path
        except Exception as e:
            logger.error(f"Error loading storage directory from config: {str(e)}")
            fallback = self.project_root / "data" / "output"
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback

    def _show_coming_soon_camera(self):
        """Show coming soon message for camera feature"""
        QMessageBox.information(
            self,
            "Coming Soon",
            "Capture with Camera feature will be available in the next update."
        )

    def _show_coming_soon_url(self):
        """Show coming soon message for URL feature"""
        QMessageBox.information(
            self,
            "Coming Soon",
            "Fetch from URL feature will be available in the next update."
        )

    def scan_from_folder(self):
        """Scan files from selected folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select folder to scan")
        if not folder:
            return
        
        try:
            p = Path(folder)
            files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS]
            
            if not files:
                QMessageBox.information(self, "No Files", "No supported image files found in the selected folder.")
                return
            
            self.add_files(files)
        except Exception as e:
            logger.error(f"Error scanning folder: {e}")
            QMessageBox.critical(self, "Error", f"Failed to scan folder: {str(e)}")

    def choose_storage_dir(self):
        """Choose storage directory and save to config"""
        folder = QFileDialog.getExistingDirectory(self, "Select storage directory")
        if folder:
            try:
                storage_path = Path(folder)
                storage_path.mkdir(parents=True, exist_ok=True)
                self.storage_path.setText(folder)

                # Lưu vào config (đúng khóa: storage_path)
                config_path = self.project_root / "config" / "app_config.json"
                config = {}
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)

                config["storage_path"] = str(storage_path)

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                logger.info(f"Storage directory updated to: {storage_path}")
            except Exception as e:
                logger.error(f"Error choosing storage directory: {e}")
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Cannot access or create the selected folder:\n{str(e)}"
                )


    def add_files(self, paths: list[Path]):
        """Add files to the list"""
        added = []
        skipped = []

        with self._files_lock:
            for p in paths:
                p = Path(p).resolve()
                
                # Validate file existence and type
                if not p.exists():
                    skipped.append(f"{p.name} (not found)")
                    continue
                
                if p.is_dir():
                    skipped.append(f"{p.name} (is directory)")
                    continue
                
                if p.suffix.lower() not in VALID_EXTENSIONS:
                    skipped.append(f"{p.name} (invalid format)")
                    continue
                
                # Check for duplicates using set (O(1) lookup)
                if p in self.files_set:
                    skipped.append(f"{p.name} (already added)")
                    continue
                
                self.files.append(p)
                self.files_set.add(p)
                added.append(p)

        # Add FileItems for new files
        if added:
            for p in added:
                # Check if item already exists to avoid duplicates
                if not any(p == f.file_path for f in self.file_list_container.findChildren(FileItem)):
                    # Get current index from total files
                    current_index = len([item for item in self.file_list_container.findChildren(FileItem)])
                    item = FileItem(current_index + 1, p, self.theme_data, self.project_root, 
                                  remove_callback=self.remove_file)
                    self.file_list_layout.addWidget(item)

        # Show feedback to user
        self.update_total_files()
        
        if added or skipped:
            feedback_msg = f"Added: {len(added)} file(s)"
            if skipped:
                feedback_msg += f"\n\nSkipped: {len(skipped)} file(s)"
                if len(skipped) <= 5:
                    feedback_msg += "\n" + "\n".join(skipped)
                else:
                    feedback_msg += "\n" + "\n".join(skipped[:5]) + f"\n... and {len(skipped) - 5} more"
            
            if added and skipped:
                QMessageBox.information(self, "Upload Status", feedback_msg)
            elif skipped:
                QMessageBox.warning(self, "Upload Status", feedback_msg)

    def remove_file(self, file_path: Path):
        """Remove file from list"""
        with self._files_lock:
            resolved_path = file_path.resolve()
            try:
                self.files.remove(file_path)
                self.files_set.discard(resolved_path)
            except ValueError:
                logger.warning(f"File not found in list: {file_path}")
        
        self.update_total_files()
        self.refresh_file_indexes()

    def refresh_file_indexes(self):
        """Update file indexes after deletion"""
        file_items = self.file_list_container.findChildren(FileItem)
        for i, item in enumerate(file_items, start=1):
            label = item.findChild(QLabel, "FileIndex")
            if label:
                label.setText(str(i))

    def update_total_files(self):
        """Update total files label and process button state"""
        self.total_files_label.setText(f"Total files: {len(self.files)}")
        self.process_btn.setEnabled(len(self.files) > 0)

    def _process_files(self):
        """Process selected files"""
        if not self.files:
            QMessageBox.warning(self, "No Files", "Please select files to process.")
            return

        reply = QMessageBox.question(
            self,
            'Process Files',
            f'Start processing {len(self.files)} file(s)?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            self.process_requested.emit(self.files)
```

## `review_page.py`
**Path:** `ocr_medical/ui/pages/review_page.py`

```python
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                                QPushButton, QFrame, QSlider, QSpinBox)
from PySide6.QtCore import Qt
from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager


class ReviewPage(BasePage):
    """
    Trang đánh giá ứng dụng
    Cho phép người dùng rating và gửi feedback
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Review", theme_manager, parent)
        
        layout = self.layout()

        rating_frame = QFrame()
        rating_frame.setObjectName("RatingFrame")
        rating_layout = QVBoxLayout(rating_frame)
        
        rating_label = QLabel("How would you rate this application?")
        rating_label.setObjectName("RatingLabel")
        rating_layout.addWidget(rating_label)
        
        stars_layout = QHBoxLayout()
        stars_layout.addStretch(1)
        
        self.rating_buttons = []
        for i in range(1, 6):
            btn = QPushButton("★")
            btn.setObjectName("StarButton")
            btn.setFixedSize(50, 50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, r=i: self._set_rating(r))
            self.rating_buttons.append(btn)
            stars_layout.addWidget(btn)
        
        stars_layout.addStretch(1)
        rating_layout.addLayout(stars_layout)
        
        self.rating_text = QLabel("No rating yet")
        self.rating_text.setObjectName("RatingText")
        self.rating_text.setAlignment(Qt.AlignCenter)
        rating_layout.addWidget(self.rating_text)
        
        layout.addWidget(rating_frame)

        feedback_label = QLabel("Your Feedback:")
        feedback_label.setObjectName("FeedbackLabel")
        layout.addWidget(feedback_label)
        
        self.feedback_text = QTextEdit()
        self.feedback_text.setObjectName("FeedbackText")
        self.feedback_text.setPlaceholderText("Share your thoughts about the application...")
        layout.addWidget(self.feedback_text)

        performance_label = QLabel("Performance Rating:")
        performance_label.setObjectName("PerformanceLabel")
        layout.addWidget(performance_label)
        
        perf_layout = QHBoxLayout()
        
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Speed:")
        speed_layout.addWidget(speed_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        speed_layout.addWidget(self.speed_slider)
        perf_layout.addLayout(speed_layout)
        
        accuracy_layout = QVBoxLayout()
        accuracy_label = QLabel("Accuracy:")
        accuracy_layout.addWidget(accuracy_label)
        self.accuracy_slider = QSlider(Qt.Horizontal)
        self.accuracy_slider.setRange(1, 10)
        self.accuracy_slider.setValue(5)
        accuracy_layout.addWidget(self.accuracy_slider)
        perf_layout.addLayout(accuracy_layout)
        
        layout.addLayout(perf_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        self.submit_btn = QPushButton("Submit Review")
        self.submit_btn.setObjectName("SubmitButton")
        self.submit_btn.clicked.connect(self._submit_review)
        btn_layout.addWidget(self.submit_btn)
        
        layout.addLayout(btn_layout)

        layout.addStretch(1)
        
        self.current_rating = 0

    def _set_rating(self, rating: int):
        self.current_rating = rating
        
        for i, btn in enumerate(self.rating_buttons):
            if i < rating:
                btn.setStyleSheet("color: #FFD700; font-size: 24px;")
            else:
                btn.setStyleSheet("color: #ddd; font-size: 24px;")
        
        rating_texts = ["", "Poor", "Fair", "Good", "Very Good", "Excellent"]
        self.rating_text.setText(f"{rating}/5 - {rating_texts[rating]}")

    def _submit_review(self):
        from PySide6.QtWidgets import QMessageBox
        
        if self.current_rating == 0:
            QMessageBox.warning(self, "No Rating", "Please select a star rating first.")
            return
        
        feedback = self.feedback_text.toPlainText()
        speed = self.speed_slider.value()
        accuracy = self.accuracy_slider.value()
        
        review_data = {
            "rating": self.current_rating,
            "feedback": feedback,
            "speed": speed,
            "accuracy": accuracy
        }
        
        QMessageBox.information(
            self, 
            "Thank You!", 
            f"Thank you for your {self.current_rating}-star review!\n\nYour feedback helps us improve."
        )
        
        self.feedback_text.clear()
        self._set_rating(0)
        self.speed_slider.setValue(5)
        self.accuracy_slider.setValue(5)
```

## `setting_page.py`
**Path:** `ocr_medical/ui/pages/setting_page.py`

```python
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout, QMessageBox, QFrame, QWidget
)
from PySide6.QtCore import Qt
from pathlib import Path
import json
import logging

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class SettingPage(BasePage):
    """Settings Page – configure API, model parameters, and storage directory."""

    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        # Header/Divider (title) do BasePage quản lý — KHÔNG style đè
        super().__init__("Settings", theme_manager, parent)
        self.theme_manager = theme_manager
        self.config_path = (
            Path(__file__).resolve().parent.parent.parent / "config" / "app_config.json"
        )

        # Lấy layout chính từ BasePage (đang chứa header + divider)
        root_layout: QVBoxLayout = self.layout()
        root_layout.setSpacing(12)

        # ===== Load config =====
        self.config = self._load_config()

        # ===== Tạo khung nội dung có scope riêng để style =====
        # => Chỉ style bên trong SettingsForm, không ảnh hưởng header của BasePage
        self.form = QFrame()
        self.form.setObjectName("SettingsForm")
        form_layout = QVBoxLayout(self.form)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # =========================
        # Theme selection
        # =========================
        theme_row = QWidget()
        theme_row_layout = QVBoxLayout(theme_row)
        theme_row_layout.setContentsMargins(0, 0, 0, 0)
        theme_row_layout.setSpacing(6)

        theme_label = QLabel("Theme:")
        theme_row_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setCurrentText(self.config.get("theme", "light"))
        # objectName để style — nhưng đã scope trong #SettingsForm
        self.theme_combo.setObjectName("SettingComboBox")
        self.theme_combo.setFocusPolicy(Qt.StrongFocus)
        # Thay theme khi đổi
        self.theme_combo.currentTextChanged.connect(self.theme_manager.set_theme)
        theme_row_layout.addWidget(self.theme_combo)

        form_layout.addWidget(theme_row)

        # =========================
        # Base URL
        # =========================
        base_row = QWidget()
        base_row_layout = QVBoxLayout(base_row)
        base_row_layout.setContentsMargins(0, 0, 0, 0)
        base_row_layout.setSpacing(6)

        base_label = QLabel("API Base URL:")
        base_row_layout.addWidget(base_label)

        self.base_input = QLineEdit()
        self.base_input.setObjectName("SettingLineEdit")
        self.base_input.setPlaceholderText("http://127.0.0.1:1234/v1")
        self.base_input.setText(self.config.get("base_url", ""))
        self.base_input.setFocusPolicy(Qt.StrongFocus)
        self.base_input.setReadOnly(False)
        self.base_input.setEnabled(True)
        base_row_layout.addWidget(self.base_input)

        form_layout.addWidget(base_row)

        # =========================
        # Temperature
        # =========================
        temp_row = QWidget()
        temp_row_layout = QVBoxLayout(temp_row)
        temp_row_layout.setContentsMargins(0, 0, 0, 0)
        temp_row_layout.setSpacing(6)

        temp_label = QLabel("Temperature:")
        temp_row_layout.addWidget(temp_label)

        self.temp_input = QLineEdit()
        self.temp_input.setObjectName("SettingLineEdit")
        self.temp_input.setPlaceholderText("0.1")
        self.temp_input.setText(str(self.config.get("temperature", 0.1)))
        self.temp_input.setFocusPolicy(Qt.StrongFocus)
        self.temp_input.setReadOnly(False)
        self.temp_input.setEnabled(True)
        temp_row_layout.addWidget(self.temp_input)

        form_layout.addWidget(temp_row)

        # =========================
        # Max Tokens
        # =========================
        token_row = QWidget()
        token_row_layout = QVBoxLayout(token_row)
        token_row_layout.setContentsMargins(0, 0, 0, 0)
        token_row_layout.setSpacing(6)

        token_label = QLabel("Max Tokens:")
        token_row_layout.addWidget(token_label)

        self.token_input = QLineEdit()
        self.token_input.setObjectName("SettingLineEdit")
        self.token_input.setPlaceholderText("1500")
        self.token_input.setText(str(self.config.get("max_tokens", 1500)))
        self.token_input.setFocusPolicy(Qt.StrongFocus)
        self.token_input.setReadOnly(False)
        self.token_input.setEnabled(True)
        token_row_layout.addWidget(self.token_input)

        form_layout.addWidget(token_row)

        # =========================
        # Storage Path
        # =========================
        store_row = QWidget()
        store_layout = QVBoxLayout(store_row)
        store_layout.setContentsMargins(0, 0, 0, 0)
        store_layout.setSpacing(6)

        store_label = QLabel("Storage Directory:")
        store_layout.addWidget(store_label)

        store_input_row = QHBoxLayout()
        store_input_row.setContentsMargins(0, 0, 0, 0)
        store_input_row.setSpacing(8)

        self.storage_input = QLineEdit()
        self.storage_input.setObjectName("SettingLineEdit")
        self.storage_input.setPlaceholderText("Leave empty to use default AppData directory")
        self.storage_input.setText(self.config.get("storage_path", ""))
        self.storage_input.setFocusPolicy(Qt.StrongFocus)
        self.storage_input.setReadOnly(False)
        self.storage_input.setEnabled(True)

        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("BrowseButton")
        browse_btn.setFocusPolicy(Qt.StrongFocus)
        browse_btn.clicked.connect(self._choose_folder)

        store_input_row.addWidget(self.storage_input)
        store_input_row.addWidget(browse_btn)
        store_layout.addLayout(store_input_row)

        form_layout.addWidget(store_row)


        form_layout.addStretch(1)

        # =========================
        # Save button
        # =========================
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("SaveButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFocusPolicy(Qt.StrongFocus)
        save_btn.clicked.connect(self._save_config)
        form_layout.addWidget(save_btn)

        # Thêm form vào root_layout (bên dưới header/divider)
        root_layout.addWidget(self.form)

        # Giữ chân trang
        

    # =========================
    # Config I/O
    # =========================
    def _load_config(self) -> dict:
        """Load configuration from app_config.json."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading config: {e}")
        return {}

    def _save_config(self):
        """Validate & save all settings to app_config.json."""
        try:
            # Validate temperature
            temp_str = (self.temp_input.text() or "").strip()
            try:
                temperature = float(temp_str) if temp_str != "" else 0.1
            except ValueError:
                QMessageBox.warning(self, "Invalid input", "Temperature must be a floating-point number.")
                self.temp_input.setFocus()
                return

            # Validate max_tokens
            tok_str = (self.token_input.text() or "").strip()
            try:
                max_tokens = int(tok_str) if tok_str != "" else 1500
            except ValueError:
                QMessageBox.warning(self, "Invalid input", "Max Tokens must be an integer.")
                self.token_input.setFocus()
                return

            # Pack config
            self.config["theme"] = self.theme_combo.currentText()
            self.config["base_url"] = self.base_input.text().strip()
            self.config["temperature"] = temperature
            self.config["max_tokens"] = max_tokens
            self.config["storage_path"] = self.storage_input.text().strip()

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)

            QMessageBox.information(self, "Saved", "Settings have been successfully updated.")
            logger.info("✅ Config saved successfully")

        except Exception as e:
            logger.error(f"Error saving config: {e}")
            QMessageBox.critical(self, "Error", f"Unable to save configuration:\n{e}")

    def _choose_folder(self):
        """Open a folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Select storage directory")
        if folder:
            self.storage_input.setText(folder)

```

## `dialogs.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/dialogs.qss.tpl`

```css

```

## `extract_info_page.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/extract_info_page.qss.tpl`

```css
/* ============================================================
   Extract Info Page – Light theme polished version (updated)
   ============================================================ */

/* --- Layout containers --- */
#BodyContainer {
    background: transparent;
    border: none;
    padding: 0;
}

#LeftPanel, #RightPanel {
    background: transparent;
    border: none;
}

/* --- Section titles --- */
#SectionLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: 700;
    color: {{ color.text.primary }};
}

/* --- Preview box --- */
#PreviewBox {
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 12px;
}

/* ============================================================
   FILE LIST AREA
   ============================================================ */
#FileScroll {
    background: transparent;
    border-left: 1px solid {{ color.border.default }};
    border-right: 1px solid {{ color.border.default }};
    border-bottom: 1px solid {{ color.border.default }};
    border-top: none;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}

#FileListContainer {
    background: transparent;
}

#FileListHeader {
    background: {{ color.background.base }};
    border: 1px solid {{ color.border.default }};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: none;
    font-weight: 600;
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}
#FileRowItem {
    border-bottom: 1px solid {{ color.border.default }};
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}
#FileRowItem:hover {
    background: {{ color.state.secondary.hover }};
}

/* ============================================================
   TAB SECTION
   ============================================================ */
#TabContainer {
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 0;
}
#TabButton {
    font-weight: 600;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    border: none;
    border-bottom: 2px solid {{ color.border.default }};
    background: transparent;
    padding: 12px 6px;
}
#TabButton:hover {
    color: {{ color.text.secondary }};
    border-bottom: 2px solid {{ color.text.secondary }};
}
#TabButton:checked {
    color: {{ color.text.secondary }};
    border-bottom: 2px solid {{ color.text.secondary }};
}

/* --- Result area --- */
#ResultBox {
    border: none;
    background: transparent;
    padding: 16px;
}
QWebEngineView#ResultContent,
QTextEdit#ResultContent {
    border: none;
    background: transparent;
    outline: none;
    padding: 8px;
    color: {{ color.text.primary }};
    font-size: 15px;
    font-family: 'Segoe UI', sans-serif;
}
#EmptyStateLabel {
    font-size: 15px;
    color: {{ color.text.muted }};
    font-style: italic;
    text-align: center;
}

/* ============================================================
   LOADING TEXT
   ============================================================ */
#LoadingText {
    font-size: 32px;
    font-weight: 600;
    color: {{ color.text.secondary }};
    text-align: center;
    padding: 8px;
}

/* ============================================================
   FOOTER BUTTONS
   ============================================================ */
#FooterButton,
#FooterStopButton,
#FooterSaveButton,
#FooterSaveAsButton {
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 700;
    border-radius: 6px;
    min-width: 110px;
    transition: all 0.2s ease-in-out;
}

/* --- STOP --- */
#FooterStopButton {
    border: none;
    color: #fff;
    background: #FE2020;
}
#FooterStopButton:hover {
    background: #FF4D4D;
    transform: scale(1.03);
}

/* --- SAVE --- */
#FooterSaveButton {
    border: none;
    color: #fff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C7BE5, stop:1 #175CD3);
}
#FooterSaveButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3D8BFF, stop:1 #1A5BE8);
}

/* --- SAVE AS --- */
#FooterSaveAsButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.primary }};
    background: #fff;
}
#FooterSaveAsButton:hover {
    background: #E9F1FF;
    border: 1px solid #2C7BE5;
    color: #175CD3;
}

/* --- DEFAULT BUTTON (Back, etc.) --- */
#FooterButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.secondary }};
    background: transparent;
}
#FooterButton:hover {
    background: {{ color.state.secondary.active }};
    color: {{ color.text.secondary }};
    border-color: {{ color.state.primary.state }};
}

/* --- DISABLED STATES --- */
#FooterStopButton:disabled,
#FooterSaveButton:disabled,
#FooterSaveAsButton:disabled,
#FooterButton:disabled {
    background: #cccccc;
    color: #999999;
    box-shadow: none;
    transform: none;
}
```

## `file_log_page.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/file_log_page.qss.tpl`

```css
#FileLogPage {
    background: #FFFFFF;
}

/* Top bar */
#SearchBar, #SortBox, #RefreshBtn {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 14px;
    background: #FFFFFF;
    color: {{ color.text.primary }};
    min-height: 32px;
}
#SearchBar:focus {
    border-color: {{ color.border.focus }};
    background: #FFFFFF;
}
#SortBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 24px;
    border-left: 1px solid {{ color.border.default }};
}
#SortBox:hover, #RefreshBtn:hover {
    background: {{ color.state.secondary.active }};
}

/* Folder Card */
#FolderCard {
    background: #FFFFFF;
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
}
#FolderCard:hover {
    border-color: {{ color.border.drag_area }};
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
#FolderName {
    font-weight: 700;
    color: {{ color.text.primary }};
    font-size: 15px;
}
#StatusBadge {
    color: #FFF;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 10px;
}

/* Buttons */
QPushButton {
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}
QPushButton#ViewBtn {
    background: {{ color.text.secondary }};
    color: #FFFFFF;
}
QPushButton#ViewBtn:hover { background: {{ color.state.primary.active }}; }
QPushButton#DeleteBtn {
    background: {{ color.border.default }};
    color: {{ color.text.primary }};
}
QPushButton#DeleteBtn:hover {
    background: {{ color.state.secondary.active }};
}
QPushButton#RefreshBtn {
    color: {{ color.text.primary }};
    background: #FFFFFF;
}

/* Pagination */
#PageBtn {
    background: #FFFFFF;
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 6px 16px;
}
#PageBtn:hover { background: {{ color.state.secondary.active }}; }
#PageLbl, #PageInfo {
    color: {{ color.text.primary }};
    font-weight: 600;
}

/* Detail Dialog */
#FileDetailDialog {
    background: #FFFFFF;
}
#LeftPanel, #RightPanel {
    background: transparent;
}
#MarkdownEditor {
    background: #FFFFFF;
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 8px;
    color: {{ color.text.primary }};
    font-family: 'Consolas';
    font-size: 14px;
}
#SaveBtn {
    background: {{ color.text.secondary }};
    color: #FFFFFF;
    border-radius: 8px;
    padding: 8px 16px;
}
#SaveBtn:hover {
    background: {{ color.state.primary.active }};
}
#ImageCompare {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: #FFFFFF;
}

```

## `home_page.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/home_page.qss.tpl`

```css
/* Home Page CSS */

#ActionButton {
    padding: 6px 10px;
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: {{ color.background.panel }};
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#ActionButton:hover {
    background: {{ color.state.secondary.hover }};
}

#UploadBox {
    border: 2px dashed {{ color.text.secondary }};
    border-radius: 12px;
    background: {{ color.background.drag_area }};
    padding: 40px;
    margin-top: 24px;
}

#UploadBox_Dragging {
    border: 2px solid {{ color.text.secondary }};
    background: rgba(23, 92, 211, 0.1);
}

#UploadText {
    margin-top: 12px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#StorageFrame {
    margin-top: 16px;
}

#FolderBox {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.panel }};
}

#StorageLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    font-weight: 600;
}

#StoragePath {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
}

#StoragePath:read-only {
    background: {{ color.background.base }};
}

#MoreButton {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.panel }};
    padding: 4px;
}

#MoreButton:hover {
    background: {{ color.state.secondary.hover }};
}

#TotalFilesLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#ProcessButton {
    background: {{ color.text.secondary }};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 8px 16px;
    font-size: 15px;
}

#ProcessButton:hover {
    background: {{ color.state.primary.hover }};
}

#ProcessButton:pressed {
    background: {{ color.state.primary.active }};
}

#ProcessButton:disabled {
    background: #cccccc;
    color: #999999;
}

#FileName {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#FileSize {
    font-size: 13px;
    color: #666;
}

#FileIndex {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    font-weight: 600;
}

#DeleteButton {
    border: 1px solid transparent;
    border-radius: 6px;
}

#DeleteButton:hover {
    background: {{ color.background.base }};
    border: 1px solid transparent;
    border-radius: 6px;
}

#FileList {
    border: none;
    background: {{ color.background.panel }};
}

#FileListContainer {
    background: {{ color.background.panel }};
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 0px;
}

#FileListHeader {
    background: {{ color.background.base }};
    border: 1px solid {{ color.border.default }};
    border-bottom: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}

#FileHeaderColumn {
    background: {{ color.background.base }};
    border-right: 1px solid {{ color.border.default }};
}

#FileHeaderColumn:last-child {
    border-right: none;
}

#FileHeaderLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    font-weight: 700;
    letter-spacing: 0.5px;
}

#FileListSeparator {
    background: {{ color.border.default }};
}

#FileItemColumn {
    background: transparent;
    border-right: 1px solid {{ color.border.default }};
}

#FileItemColumn:last-child {
    border-right: none;
}

#FileItem {
    border-bottom: 1px solid {{ color.border.default }};
}

#FileItem:last-child {
    border-bottom: none;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}
```

## `review_page.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/review_page.qss.tpl`

```css
/* Review Page CSS */

#RatingFrame {
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 20px;
    background: {{ color.background.panel }};
    margin-bottom: 16px;
}

#RatingLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
    margin-bottom: 12px;
}

#StarButton {
    background: transparent;
    border: none;
    font-size: 32px;
    color: #ddd;
}

#StarButton:hover {
    color: #FFD700;
}

#RatingText {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.muted }};
    margin-top: 8px;
}

#FeedbackLabel, #PerformanceLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
    margin-top: 12px;
    margin-bottom: 8px;
}

#FeedbackText {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 12px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
    min-height: 120px;
}

#SubmitButton {
    background: {{ color.text.secondary }};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-size: {{ typography.normal.size }}px;
    font-weight: 700;
}

#SubmitButton:hover {
    background: {{ color.state.primary.hover }};
}
```

## `setting_page.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/setting_page.qss.tpl`

```css
/* ============================================================
   Settings Page – scoped styles
   Only apply to content inside #SettingsForm
   ============================================================ */

#SettingsForm QLabel {
    font-size: 15px;
    font-weight: 600;
    color: {{ color.text.primary }};
    margin-top: 6px;
}

#SettingsForm QLineEdit#SettingLineEdit {
    background: #fff;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 14px;
    color: {{ color.text.primary }};
}

#SettingsForm QLineEdit#SettingLineEdit:focus {
    border: 1px solid {{ color.border.focus }};
}

#SettingsForm QComboBox#SettingComboBox {
    background: #fff;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 14px;
}

#SettingsForm QComboBox#SettingComboBox::drop-down {
    width: 24px;
    border: none;
}

#SettingsForm QPushButton#BrowseButton {
    padding: 8px 16px;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: #f8f9fa;
}

#SettingsForm QPushButton#BrowseButton:hover {
    background: #e9ecef;
}

#SettingsForm QPushButton#SaveButton {
    margin-top: 16px;
    padding: 8px 16px;
    font-weight: 700;
    border-radius: 6px;
    color: #fff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C7BE5, stop:1 #175CD3);
}

#SettingsForm QPushButton#SaveButton:hover {
    background: #357ABD;
}

#SettingsForm QPushButton#SaveButton:pressed {
    background: #2C5AA0;
}

```

## `style.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/style.qss.tpl`

```css
/* ****************** */
/*   1. Main Window   */
/* ****************** */

#MainWindow {
    background: {{ color.background.base }};
}


/* ****************** */
/*   2. Panel Chung   */
/* ****************** */

#Panel {
    background: {{ color.background.panel }};
    padding: 12px;
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
}


/* ****************** */
/*   3. Side Panel    */
/* ****************** */

/* 3.1 Navigation Buttons */
QPushButton[nav="true"] {
    text-align: left;
    padding: 12px 16px;
    background: transparent;

    border-radius: 12px;
    border: 1px solid transparent;

    font-size: {{ typography.secondary.size }}px;
    font-weight: {{ typography.secondary.weight }};
    color: {{ color.text.primary }};
}

QPushButton[nav="true"]:hover {
    background: {{ color.state.secondary.hover }};
    border: 1px solid #e3e5e6ff;
}

QPushButton[nav="true"]:checked {
    background: {{ color.state.secondary.active }};
    color: {{ color.text.secondary }};
}

/* 3.2 User Info */
#UserLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#VersionLabel {
    font-size: {{ typography.muted.size }}px;
    color: {{ color.text.muted }};
}

/* ****************** */
/*   4. Base Page     */
/* ****************** */

#PageHeader {
    font-size: {{ typography.heading1.size }}px;
    font-weight: {{ typography.heading1.weight }};
    color: {{ color.text.primary }};
}

#Divider {
    background: {{ color.border.default }};
    border: none;
    margin-top: 2px;
    margin-bottom: 2px;
}

* {
    outline: none;
}

QWidget {
    outline: none;
}

QPushButton:focus,
QLineEdit:focus,
QTextEdit:focus,
QComboBox:focus {
    outline: none;
    border: 1px solid {{ color.border.default }};
}
```

## `theme_light.json`
**Path:** `ocr_medical/ui/style/theme/theme_light.json`

```json
{
  "theme": {
    "name": "light",
    "version": "1.0.0",
    "author": "Minh Khanh",
    "description": "A light theme for the medical OCR application."
  },
  "color": {
    "background": {
      "base": "#F6F8FB",
      "panel": "#FFFFFF",
      "drag_area": "#ECF2FE"
    },
    "text": {
      "primary": "#1C1C1C",
      "secondary": "#175CD3",
      "muted": "#ADB5BD",
      "placeholder": "#777777"
    },
    "border": {
      "default": "#ECE9E9",
      "search_bar": "#777777",
      "focus": "#4A90E2",
      "drag_area": "#A0C4FF"
    },
    "state": {
      "primary": {
        "hover": "#357ABD",
        "active": "#2C5AA0",
        "focus": "#8B8B8B"
      },
      "secondary": {
        "hover": "#F7F4F4",
        "active": "#ECF2FE" 
      }
    }
  },
  "typography": {
    "family": "Inter",
    "heading1": { "size": 25, "weight": 800 },
    "heading2": { "size": 16, "weight": 800 },
    "normal":   { "size": 14, "weight": 400 },
    "secondary":{ "size": 16, "weight": 800 },
    "muted":    { "size": 12, "weight": 400 },
    "placeholder": { "size": 14, "weight": 500 }
  }
}

```

## `dialog_manager.py`
**Path:** `ocr_medical/ui/widgets/dialog_manager.py`

```python
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
```

## `side_panel.py`
**Path:** `ocr_medical/ui/widgets/side_panel.py`

```python
from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem, QPushButton

from ocr_medical.ui.style.style_loader import load_svg_colored
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.utils.path_helper import resource_path


# ============================================================
#                     NavButton
# ============================================================
class NavButton(QWidget):
    """Custom nav button với icon đổi màu theo trạng thái"""

    def __init__(self, key: str, text: str, icon_path: Path, theme_data: dict, parent=None):
        super().__init__(parent)

        # Tạo QPushButton
        self.btn = QPushButton(f"  {text}", self)
        self.btn.setObjectName(f"NavBtn__{key}")
        self.btn.setProperty("nav", True)
        self.btn.setCheckable(True)
        self.btn.setAutoExclusive(True)
        self.btn.setCursor(Qt.PointingHandCursor)
        self.btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Lưu thông tin
        self.icon_path = icon_path
        self.normal_color = theme_data["color"]["text"]["primary"]
        self.hover_color = theme_data["color"]["text"]["primary"]
        self.active_color = theme_data["color"]["text"]["secondary"]

        # Set icon mặc định
        if self.icon_path.exists():
            self.btn.setIcon(load_svg_colored(self.icon_path, self.normal_color, 20))
            self.btn.setIconSize(QSize(20, 20))

        # Khi toggle (active)
        self.btn.toggled.connect(self._on_toggled)

        # Override hover
        self.btn.enterEvent = self._on_enter
        self.btn.leaveEvent = self._on_leave

    def widget(self):
        return self.btn

    def _on_toggled(self, checked: bool):
        """Đổi màu icon khi active / inactive"""
        if self.icon_path.exists():
            color = self.active_color if checked else self.normal_color
            self.btn.setIcon(load_svg_colored(self.icon_path, color, 20))

    def _on_enter(self, event):
        """Đổi màu icon khi hover"""
        if self.icon_path.exists() and not self.btn.isChecked():
            self.btn.setIcon(load_svg_colored(self.icon_path, self.hover_color, 20))
        QPushButton.enterEvent(self.btn, event)

    def _on_leave(self, event):
        """Trả lại màu icon khi rời hover"""
        if self.icon_path.exists() and not self.btn.isChecked():
            self.btn.setIcon(load_svg_colored(self.icon_path, self.normal_color, 20))
        QPushButton.leaveEvent(self.btn, event)


# ============================================================
#                     SidePanel
# ============================================================
class SidePanel(QWidget):
    page_selected = Signal(str)

    def __init__(self, project_root: Path, theme_manager: ThemeManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SidePanel")

        self.theme_manager = theme_manager
        theme_data = theme_manager.get_theme_data()
        self.version = theme_data["theme"]["version"]

        # Layout chính
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # --- Logo ---
        logo_path = resource_path("ocr_medical/assets/logo/logo-text.png")
        logo_label = QLabel()
        logo_pixmap = QPixmap(str(logo_path))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaledToWidth(100, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(logo_label)

        layout.addItem(QSpacerItem(0, 60, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # --- Navigation buttons ---
        self.buttons: dict[str, NavButton] = {}
        pages = [
            ("home", "Home", "home.svg"),
            ("extra_info", "Extract Info", "scan.svg"),
            ("file_log", "File Log", "folder.svg"),
            ("setting", "Setting", "setting.svg"),
            ("review", "Review", "review.svg"),
        ]

        for key, text, icon_file in pages:
            icon_path = resource_path(f"ocr_medical/assets/icon/{icon_file}")
            nav_btn = NavButton(key, text, icon_path, theme_data)
            nav_btn.btn.clicked.connect(lambda checked, k=key: self.page_selected.emit(k))

            layout.addWidget(nav_btn.widget())
            self.buttons[key] = nav_btn

        layout.addStretch(1)

        # --- User info at bottom ---
        user_icon_path = resource_path("ocr_medical/assets/icon/user.svg")
        user_icon_label = QLabel()
        if user_icon_path.exists():
            user_icon_label.setPixmap(
                load_svg_colored(user_icon_path, theme_data["color"]["text"]["primary"], 24).pixmap(24, 24)
            )
        user_icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(user_icon_label)

        user_label = QLabel("User/Administrator")
        user_label.setObjectName("UserLabel")
        user_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(user_label)

        version_label = QLabel(f"Version {self.version}")
        version_label.setObjectName("VersionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Default active
        if "home" in self.buttons:
            self.buttons["home"].btn.setChecked(True)

    def set_active(self, key: str) -> None:
        """Đặt trạng thái active cho button theo key"""
        if key in self.buttons:
            self.buttons[key].btn.setChecked(True)

```

## `main_window.py`
**Path:** `ocr_medical/ui/main_window.py`

```python
from __future__ import annotations
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QStackedWidget, QFrame

from pathlib import Path

from ocr_medical.ui.widgets.side_panel import SidePanel
from ocr_medical.ui.pages.home_page import HomePage
from ocr_medical.ui.pages.setting_page import SettingPage
from ocr_medical.ui.pages.file_log_page import FileLogPage
from ocr_medical.ui.pages.extract_info_page import ExtraInfoPage
from ocr_medical.ui.pages.review_page import ReviewPage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_theme_qss


MARGIN = 24
GUTTER = 24
SIDE_COLS = 2
TOTAL_COLS = 12
MAIN_COLS = TOTAL_COLS - SIDE_COLS
TOTAL_ROWS = 12


class Panel(QFrame):
    """Khung panel có border / nền đồng nhất theo theme."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path, theme_name: str = "light") -> None:
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle("OCR-Medical")

        logo_path = self.project_root / "assets" / "logo" / "logo.png"
        if logo_path.exists():
            self.setWindowIcon(QIcon(str(logo_path)))

        self.theme_manager = ThemeManager(theme_name)
        self.theme_manager.theme_changed.connect(self.apply_theme)

        root = QWidget(self)
        self.setObjectName("MainWindow")
        self.setCentralWidget(root)

        grid = QGridLayout(root)
        grid.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        grid.setHorizontalSpacing(GUTTER)
        grid.setVerticalSpacing(GUTTER)

        for c in range(TOTAL_COLS):
            grid.setColumnStretch(c, 1)
        for r in range(TOTAL_ROWS):
            grid.setRowStretch(r, 1)

        self.side_panel = SidePanel(
            project_root=self.project_root,
            theme_manager=self.theme_manager
        )
        side_wrapper = Panel()
        from PySide6.QtWidgets import QGridLayout as QGL
        side_layout = QGL(side_wrapper)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.addWidget(self.side_panel, 0, 0, 1, 1)

        self.stack = QStackedWidget()
        main_wrapper = Panel()
        main_layout = QGL(main_wrapper)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack, 0, 0, 1, 1)

        grid.addWidget(side_wrapper, 0, 0, TOTAL_ROWS, SIDE_COLS)
        grid.addWidget(main_wrapper, 0, SIDE_COLS, TOTAL_ROWS, MAIN_COLS)

        self.page_index: dict[str, int] = {}

        home_page = HomePage(self.theme_manager)
        home_page.process_requested.connect(self._go_to_extract_info)
        self._add_page("home", home_page)

        self._add_page("setting", SettingPage(self.theme_manager))
        self._add_page("file_log", FileLogPage(self.theme_manager))

        extract_page = ExtraInfoPage(self.theme_manager)
        extract_page.navigate_back_requested.connect(
            lambda: self.navigate_to("home"))
        self._add_page("extra_info", extract_page)

        self._add_page("review", ReviewPage(self.theme_manager))

        self.side_panel.page_selected.connect(self.navigate_to)

        self.navigate_to("home")

        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name()
        )

    def disable_focus_policy(self):
        """Disable focus policy cho toàn bộ ứng dụng"""
        self.set_focus_policy_recursive(self, Qt.NoFocus)

    @staticmethod
    def set_focus_policy_recursive(widget, policy):
        """Recursively set focus policy cho tất cả children"""
        widget.setFocusPolicy(policy)
        for child in widget.findChildren(QWidget):
            child.setFocusPolicy(policy)

    def _add_page(self, key: str, widget: QWidget) -> None:
        idx = self.stack.addWidget(widget)
        self.page_index[key] = idx

    def navigate_to(self, key: str) -> None:
        if key in self.page_index:
            self.stack.setCurrentIndex(self.page_index[key])
            self.side_panel.set_active(key)

    def _go_to_extract_info(self, files: list[Path]):
        self.navigate_to("extra_info")

        page = self.stack.widget(self.page_index["extra_info"])
        if hasattr(page, "load_files"):
            page.load_files(files)

    def apply_theme(self, theme_data: dict, theme_name: str) -> None:
        qss = load_theme_qss(theme_name)
        self.setStyleSheet(qss)

```

## `main.py`
**Path:** `ocr_medical/main.py`

```python
from __future__ import annotations
import sys
import json
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication
from ocr_medical.ui.main_window import MainWindow

CONFIG_FILE = Path(__file__).resolve().parent / "config" / "app_config.json"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(data: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    app = QApplication(sys.argv)
    project_root = Path(__file__).resolve().parent
    config = load_config()
    theme_name = config.get("theme", "light")

    win = MainWindow(project_root, theme_name)

    screens = QGuiApplication.screens()
    idx = min(config.get("last_screen", 0), len(screens) - 1)
    geom = config.get("geometry")
    if geom:
        x, y, w, h = geom
        win.setGeometry(x, y, w, h)
    else:
        win.setGeometry(screens[idx].geometry())

    if config.get("is_fullscreen"):
        win.showFullScreen()
    elif config.get("is_maximized"):
        win.showMaximized()
    else:
        win.show()

    def on_quit():
        screen = win.windowHandle().screen()
        idx = screens.index(screen) if screen in screens else 0
        data = {
            "last_screen": idx,
            "geometry": [win.geometry().x(), win.geometry().y(),
                         win.geometry().width(), win.geometry().height()],
            "is_maximized": win.isMaximized(),
            "is_fullscreen": win.isFullScreen(),
            "theme": win.theme_manager.get_theme_name(),
        }
        save_config(data)

    app.aboutToQuit.connect(on_quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

```

## `pipeline.py`
**Path:** `ocr_medical/core/pipeline.py`

```python
from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
import requests
import json
from PIL import Image
from PySide6.QtCore import QStandardPaths

from ocr_medical.core.waifu2x_loader import load_waifu2x
from ocr_medical.core.process_image import process_image
from ocr_medical.core.ocr_extract import call_qwen_ocr
from ocr_medical.core.status import status_manager
from ocr_medical.utils.path_helper import resource_path

# ============================================================
# 📁 Project root (được dùng khi fallback)
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ============================================================
# 🧠 Prompt mặc định cho OCR
# ============================================================
DEFAULT_PROMPT = (
    "Hãy trích xuất toàn bộ nội dung văn bản có trong ảnh, bao gồm cả chữ, số, ký hiệu đặc biệt "
    "và các cấu trúc bảng nếu có. "
    "Yêu cầu trình bày kết quả như sau:\n"
    "1. Nếu ảnh chứa bảng dữ liệu:\n"
    "   - Trình bày lại dưới dạng **bảng Markdown** với định dạng rõ ràng.\n"
    "   - Hàng tiêu đề in đậm.\n"
    "   - Các cột căn chỉnh bằng dấu | và khoảng trắng đều.\n"
    "   - Các mục quan trọng (ví dụ: MIỄN DỊCH, PXN VI SINH) phải in đậm.\n"
    "   - Giữ nguyên ký hiệu đặc biệt (ví dụ dấu * phải hiển thị là \\*).\n"
    "   - Giá trị số và đơn vị giữ nguyên định dạng gốc.\n"
    "2. Nếu ảnh **không chứa bảng** mà chỉ có đoạn văn, chữ viết hoặc ký tự rời:\n"
    "   - Hãy trích xuất toàn bộ văn bản đúng theo thứ tự hiển thị từ trên xuống dưới, trái sang phải.\n"
    "   - Giữ nguyên ngắt dòng, dấu câu và ký hiệu đặc biệt.\n"
    "   - Không thêm lời giải thích hay định dạng Markdown.\n"
    "Kết quả chỉ bao gồm phần nội dung đã trích xuất, không thêm mô tả hoặc phân tích."
)


# ============================================================
# 📦 Lấy thư mục output mặc định từ config
# ============================================================
def get_default_output() -> Path:
    """
    Load default output directory từ config file.
    Nếu không có thì dùng AppData hoặc fallback về project/data/output.
    """
    try:
        config_path = resource_path("ocr_medical/config/app_config.json")
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                storage_dir_str = config.get("storage_path", "")

                if storage_dir_str and storage_dir_str.strip():
                    storage_path = Path(storage_dir_str)
                    storage_path.mkdir(parents=True, exist_ok=True)
                    return storage_path

        # Nếu không có config hoặc storage_path trống → AppData
        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        default_path = Path(app_data) / "OCR-Medical" / "output"
        default_path.mkdir(parents=True, exist_ok=True)
        return default_path

    except Exception as e:
        # Nếu lỗi, fallback về thư mục dự án
        status_manager.add(f"⚠️ Lỗi load storage path: {e}")
        fallback_path = PROJECT_ROOT / "data" / "output"
        fallback_path.mkdir(parents=True, exist_ok=True)
        return fallback_path


# 🗂️ Output mặc định
DEFAULT_OUTPUT = get_default_output()


# ============================================================
# ✏️ Gọi OCR và lưu kết quả Markdown
# ============================================================
def save_text(processed_path: Path, img_name: str, output_root: Path):
    """
    Gọi OCR và lưu kết quả Markdown.
    """
    try:
        out_dir_text = output_root / img_name / "text"
        out_dir_text.mkdir(parents=True, exist_ok=True)

        extracted = call_qwen_ocr(str(processed_path), DEFAULT_PROMPT)
        ocr_path = out_dir_text / f"{img_name}_processed.md"
        with open(ocr_path, "w", encoding="utf-8") as f:
            f.write(extracted)

        status_manager.add(f"✅ Đã lưu kết quả OCR: {ocr_path.name}")
    except Exception as e:
        status_manager.add(f"❌ Lỗi lưu OCR: {e}")
        raise


# ============================================================
# 🔄 Pipeline chính
# ============================================================
def process_input(input_path: str, output_root: str = None):
    """
    Pipeline OCR:
    - Input: file ảnh, folder, hoặc URL
    - Output: original, processed, text (.md)
    """
    status_manager.reset()
    output_root = Path(output_root) if output_root else DEFAULT_OUTPUT
    upscaler = load_waifu2x()

    try:
        # Nếu là URL
        if input_path.startswith(("http://", "https://")):
            response = requests.get(input_path)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
            img_name = Path(urlparse(input_path).path).stem
            _, proc_path = process_image(upscaler, img, img_name, output_root)
            save_text(proc_path, img_name, output_root)
            return status_manager

        # Nếu là file ảnh
        p = Path(input_path)
        if p.is_file():
            img = Image.open(p).convert("RGB")
            img_name = p.stem
            _, proc_path = process_image(upscaler, img, img_name, output_root)
            save_text(proc_path, img_name, output_root)

        # Nếu là thư mục
        elif p.is_dir():
            for file in p.glob("*.*"):
                if file.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                    img = Image.open(file).convert("RGB")
                    img_name = file.stem
                    _, proc_path = process_image(upscaler, img, img_name, output_root)
                    save_text(proc_path, img_name, output_root)
        else:
            status_manager.add(f"❌ Input không tồn tại: {input_path}")
            raise FileNotFoundError(f"Input {input_path} không tồn tại")

        return status_manager

    except Exception as e:
        status_manager.add(f"❌ Pipeline error: {e}")
        raise

```

## `ocr_extract.py`
**Path:** `ocr_medical/core/ocr_extract.py`

```python
import base64
import json
import requests
from pathlib import Path
from ocr_medical.core.status import status_manager
from ocr_medical.utils.path_helper import resource_path


# =====================================================
#   Load configuration safely (for .py and .exe)
# =====================================================
def load_config() -> dict:
    """
    Đọc config từ ocr_medical/config/app_config.json
    (tự động tương thích PyInstaller)
    """
    config_path = resource_path("ocr_medical/config/app_config.json")

    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                status_manager.add("⚙️ Config loaded successfully.")
                return data
        else:
            status_manager.add("⚠️ Config file not found, using defaults.")
            return {}
    except Exception as e:
        status_manager.add(f"❌ Error reading config: {e}")
        return {}


# =====================================================
#   Global configuration values
# =====================================================
CONFIG = load_config()

BASE_URL = CONFIG.get("base_url", "http://127.0.0.1:1234/v1")
MODEL_ID = CONFIG.get("model_id", "qwen/qwen2.5-vl-7b")
TEMPERATURE = CONFIG.get("temperature", 0.1)
MAX_TOKENS = CONFIG.get("max_tokens", 1500)
STREAM = CONFIG.get("stream", False)
IS_MAXIMIZED = CONFIG.get("is_maximized", True)


# =====================================================
#   Helper functions
# =====================================================
def infer_mime_from_filename(filename: str) -> str:
    low = filename.lower()
    if low.endswith(".png"):
        return "image/png"
    if low.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if low.endswith(".webp"):
        return "image/webp"
    return "application/octet-stream"


def to_data_url(path: str) -> str:
    """
    Đọc file ảnh và encode thành data URL (base64)
    """
    try:
        abs_path = Path(path).resolve()
        if not abs_path.exists():
            raise FileNotFoundError(f"Image not found: {abs_path}")
        mime = infer_mime_from_filename(abs_path.name)
        with open(abs_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    except Exception as e:
        status_manager.add(f"❌ Error encoding image: {e}")
        raise


# =====================================================
#   OCR call to Qwen API
# =====================================================
def call_qwen_ocr(image_path: str, prompt_text: str) -> str:
    """
    Gọi API Qwen OCR với ảnh đã xử lý (png/jpg/jpeg/webp)
    """
    url = f"{BASE_URL}/chat/completions"
    image_url = to_data_url(image_path)

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": STREAM,
    }
    headers = {"Content-Type": "application/json"}

    try:
        status_manager.add(f"🔄 Sending OCR request: {Path(image_path).name}")
        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=180)
        resp.raise_for_status()
        data = resp.json()

        if "choices" not in data or not data["choices"]:
            raise ValueError("Invalid OCR response (no 'choices').")

        result = data["choices"][0]["message"]["content"]
        status_manager.add("✅ OCR completed successfully.")
        return result

    except requests.exceptions.ConnectionError:
        status_manager.add("❌ Connection failed. Check BASE_URL or network.")
        raise
    except Exception as e:
        status_manager.add(f"❌ OCR failed: {e}")
        raise


# =====================================================
#   Window state helper
# =====================================================
def get_window_state():
    """
    Trả về trạng thái hiển thị mặc định khi khởi động app
    """
    if IS_MAXIMIZED:
        return "maximized"
    return "normal"

```

## `process_image.py`
**Path:** `ocr_medical/core/process_image.py`

```python
from pathlib import Path
from PIL import Image
from ocr_medical.core.status import status_manager


def save_original(img: Image.Image, img_name: str, output_root: Path) -> Path:
    """
    Lưu ảnh gốc vào output/{img_name}/original
    """
    try:
        out_dir = output_root / img_name / "original"
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{img_name}_original.png"
        img.save(path)
        status_manager.add("✅ Lưu ảnh gốc (original)")
        return path
    except Exception as e:
        status_manager.add(f"❌ Lỗi lưu ảnh gốc: {e}")
        raise


def enhance_image(upscaler, img: Image.Image, img_name: str, output_root: Path) -> Path:
    """
    Xử lý ảnh bằng Waifu2x và lưu vào output/{img_name}/processed
    """
    try:
        out_dir = output_root / img_name / "processed"
        out_dir.mkdir(parents=True, exist_ok=True)
        enhanced = upscaler(img)
        path = out_dir / f"{img_name}_processed.png"
        enhanced.save(path)
        status_manager.add("✅ Xử lý ảnh (processed)")
        return path
    except Exception as e:
        status_manager.add(f"❌ Lỗi xử lý ảnh: {e}")
        raise


def process_image(upscaler, img: Image.Image, img_name: str, output_root: Path) -> tuple[Path, Path]:
    """
    Trả về (path ảnh gốc, path ảnh đã xử lý)
    """
    orig = save_original(img, img_name, output_root)
    proc = enhance_image(upscaler, img, img_name, output_root)
    return orig, proc

```

## `status.py`
**Path:** `ocr_medical/core/status.py`

```python
from typing import List

class StatusManager:
    """
    Quản lý thông báo cho pipeline.
    """
    def __init__(self):
        self.messages: List[str] = []
        self.logs: List[str] = []
        self.state: str = ""

    def add(self, msg: str):
        print(msg)
        self.messages.append(msg)
        self.logs.append(msg)
        self.state = msg

    def reset(self):
        self.messages.clear()
        self.logs.clear()
        self.state = ""

# Singleton
status_manager = StatusManager()
```

## `waifu2x_loader.py`
**Path:** `ocr_medical/core/waifu2x_loader.py`

```python
import torch
import json
import logging
from pathlib import Path
from ocr_medical.core.status import status_manager
from ocr_medical.utils.path_helper import resource_path

logger = logging.getLogger(__name__)

# ============================================================
#  Utility: Device selection
# ============================================================
def get_device_from_config():
    """Chọn thiết bị dựa theo app_config.json (auto / cpu / cuda)."""
    try:
        config_path = Path(__file__).resolve().parent.parent / "config" / "app_config.json"
        device_pref = "auto"

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                device_pref = cfg.get("device_preference", "auto").lower()

        if device_pref == "cpu":
            device = torch.device("cpu")
            status_manager.add("⚙️ Running on CPU (forced by config)")
        elif device_pref == "cuda":
            if torch.cuda.is_available():
                device = torch.device("cuda")
                status_manager.add("🚀 Using GPU (CUDA) as configured")
            else:
                device = torch.device("cpu")
                status_manager.add("⚠️ GPU not available. Falling back to CPU.")
        else:  # auto
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            if device.type == "cuda":
                status_manager.add("🚀 GPU detected — using CUDA for processing")
            else:
                status_manager.add("⚙️ No GPU found — using CPU")

        logger.info(f"[Waifu2x] Selected device: {device}")
        return device

    except Exception as e:
        logger.error(f"Error reading config for device selection: {e}")
        status_manager.add("⚠️ Defaulting to CPU due to config error")
        return torch.device("cpu")


# ============================================================
#  Main: Load Waifu2x model (Local first, fallback GitHub)
# ============================================================
def load_waifu2x(
    # ---- Model options ----
    model_type="art_scan",     # 'art', 'photo', 'art_scan'
    method="noise_scale",      # 'scale', 'noise', 'noise_scale', 'auto_scale'
    noise_level=3,             # -1=off, 0=none, 1=low, 2=medium, 3=high
    scale=2,                   # 1, 1.6, 2, 4

    # ---- Performance options ----
    tile_size=64,              # 64/128/256 (smaller for low VRAM)
    batch_size=4,              # parallel tiles
    amp=True,                  # use FP16 if available
):
    """
    Load Waifu2x model — ưu tiên local repo, fallback GitHub nếu thiếu.
    """
    try:
        device = get_device_from_config()
        device_ids = [0] if device.type == "cuda" else [-1]

        # ==== ƯU TIÊN LOCAL ====
        local_repo = resource_path("ocr_medical/core/models/nunif/nagadomi_nunif_master")

        if Path(local_repo).exists() and (Path(local_repo) / "waifu2x" / "hubconf.py").exists():
            status_manager.add("📦 Loading Waifu2x model from local repository...")
            logger.info(f"[Waifu2x] Loading local repo at: {local_repo}")

            upscaler = torch.hub.load(
                str(local_repo),
                'waifu2x',
                source='local',
                model_type=model_type,
                method=method,
                noise_level=noise_level,
                scale=scale,
                tile_size=tile_size,
                batch_size=batch_size,
                amp=amp
            )

            status_manager.add("✅ Waifu2x model loaded successfully (LOCAL mode).")
            logger.info("[Waifu2x] Model loaded locally.")
        else:
            # ==== FALLBACK ONLINE ====
            status_manager.add("🌐 Local repo missing — downloading via torch.hub...")
            logger.warning("[Waifu2x] Local repo not found. Downloading from GitHub...")

            upscaler = torch.hub.load(
                'nagadomi/nunif',
                'waifu2x',
                source='github',
                model_type=model_type,
                method=method,
                noise_level=noise_level,
                scale=scale,
                tile_size=tile_size,
                batch_size=batch_size,
                amp=amp
            )

            status_manager.add("✅ Waifu2x model downloaded successfully (ONLINE mode).")
            logger.info("[Waifu2x] Model downloaded from GitHub.")

        # ==== Chuyển thiết bị (GPU/CPU) ====
        if hasattr(upscaler, "to"):
            upscaler = upscaler.to(device)

        status_manager.add(f"🚀 Ready — Waifu2x running on {device.type.upper()}")
        logger.info(f"[Waifu2x] Model ready on {device.type}")
        return upscaler

    except Exception as e:
        logger.error(f"[Waifu2x] Error loading model: {e}")
        status_manager.add(f"❌ Failed to load Waifu2x model: {e}")
        raise

```

## `app_config.json`
**Path:** `ocr_medical/config/app_config.json`

```json
{
  "base_url": "http://192.168.1.12:1234/v1",
  "temperature": 0.1,
  "max_tokens": 1500,
  "stream": false,
  "storage_path": "",
  "theme": "light",
  "is_maximized": true
}

```

## `logger.py`
**Path:** `ocr_medical/utils/logger.py`

```python

```
