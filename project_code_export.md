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
    QStackedWidget, QScrollArea, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QSize
from pathlib import Path

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored


# =====================================================
#             File Row Item (giống HomePage)
# =====================================================
class FileRowItem(QFrame):
    """Một hàng trong danh sách file gồm: index, file name, status"""
    def __init__(self, index: int, file_name: str, state: str, project_root: Path):
        super().__init__()
        self.setObjectName("FileRowItem")
        self.project_root = project_root

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(0)

        # ----- Cột 1: Index -----
        index_lbl = QLabel(str(index))
        index_lbl.setObjectName("FileIndex")
        index_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(index_lbl, 1)

        # ----- Cột 2: File Name -----
        name_lbl = QLabel(file_name)
        name_lbl.setObjectName("FileName")
        layout.addWidget(name_lbl, 5)

        # ----- Cột 3: Status -----
        status_widget = self._create_status_label(state)
        layout.addWidget(status_widget, 3)

    def _create_status_label(self, state: str) -> QWidget:
        """Tạo icon tròn + chữ trạng thái"""
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
        text_lbl.setStyleSheet("color: #475569; font-weight: 500;")

        container = QWidget()
        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        lay.addWidget(icon_lbl)
        lay.addWidget(text_lbl)
        lay.addStretch()
        return container


# =====================================================
#                 Extract Info Page
# =====================================================
class ExtraInfoPage(BasePage):
    navigate_back_requested = Signal()
    stop_ocr_requested = Signal()
    save_requested = Signal()

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__("Extraction Info", theme_manager, parent)

        self.theme_manager = theme_manager
        self.theme_data = theme_manager.get_theme_data()
        self.project_root = Path(__file__).resolve().parent.parent.parent

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

        self.more_btn = QPushButton()
        self.more_btn.setObjectName("MoreButton")
        self.more_btn.setFixedSize(32, 32)
        self.more_btn.setCursor(Qt.PointingHandCursor)

        more_icon = self.project_root / "assets" / "icon" / "more.svg"
        if more_icon.exists():
            self.more_btn.setIcon(
                load_svg_colored(more_icon, self.theme_data["color"]["text"]["primary"], 18)
            )
        header_layout.addWidget(self.more_btn)
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

        # Header (giống HomePage)
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
        tab1 = QLabel("📄 Rendered Markdown Preview Area")
        tab1.setObjectName("ResultBox")
        tab1.setAlignment(Qt.AlignCenter)
        tab2 = QLabel("✏️ Raw Markdown Text Area")
        tab2.setObjectName("ResultBox")
        tab2.setAlignment(Qt.AlignCenter)
        self.tab_stack.addWidget(tab1)
        self.tab_stack.addWidget(tab2)
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

        self.back_btn = QPushButton("Back")
        self.back_btn.setObjectName("FooterButton")
        self.back_btn.setIcon(load_svg_colored(self.project_root / "assets" / "icon" / "back-page.svg", "#175CD3", 16))
        self.back_btn.setIconSize(QSize(16, 16))
        self.back_btn.clicked.connect(lambda: self.navigate_back_requested.emit())

        self.stop_btn = QPushButton("Stop OCR")
        self.stop_btn.setObjectName("FooterStopButton")
        self.stop_btn.setIcon(load_svg_colored(self.project_root / "assets" / "icon" / "stop_ocr.svg", "#777777", 16))
        self.stop_btn.setIconSize(QSize(16, 16))
        self.stop_btn.clicked.connect(lambda: self.stop_ocr_requested.emit())

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("FooterSaveButton")
        self.save_btn.setIcon(load_svg_colored(self.project_root / "assets" / "icon" / "save.svg", "#FFFFFF", 16))
        self.save_btn.setIconSize(QSize(16, 16))
        self.save_btn.clicked.connect(lambda: self.save_requested.emit())

        left_group = QHBoxLayout()
        left_group.setSpacing(8)
        left_group.addWidget(self.back_btn)
        left_group.addWidget(self.stop_btn)
        footer.addLayout(left_group)
        footer.addStretch(1)
        footer.addWidget(self.save_btn, alignment=Qt.AlignRight)
        layout.addLayout(footer)

    # =====================================================
    #                     LOGIC
    # =====================================================
    def _switch_tab(self, index: int):
        self.tab_stack.setCurrentIndex(index)
        self.tab1_btn.setChecked(index == 0)
        self.tab2_btn.setChecked(index == 1)

    def load_files(self, files: list[Path]):
        """Hiển thị danh sách file theo cấu trúc mới"""
        self.clear_files()
        for idx, f in enumerate(files, start=1):
            row = FileRowItem(idx, f.name, "waiting", self.project_root)
            self.file_container_layout.addWidget(row)

    def clear_files(self):
        """Xóa toàn bộ hàng file hiện tại"""
        while self.file_container_layout.count():
            item = self.file_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

```

## `file_log_page.py`
**Path:** `ocr_medical/ui/pages/file_log_page.py`

```python
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                                QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                                QMessageBox, QFrame, QDialog, QTabWidget, QTextEdit,
                                QListWidget, QListWidgetItem, QComboBox, QDoubleSpinBox)
from PySide6.QtCore import Qt, QSize, QMimeData
from PySide6.QtGui import QAction, QColor, QClipboard, QGuiApplication
from PySide6.QtWidgets import QApplication
from pathlib import Path
import json
from datetime import datetime

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored


class FileDetailDialog(QDialog):
    """Dialog hiển thị chi tiết folder"""
    def __init__(self, folder: Path, theme_data: dict, parent=None):
        super().__init__(parent)
        self.folder = folder
        self.theme_data = theme_data
        self.setWindowTitle(f"Details - {folder.name}")
        self.setGeometry(100, 100, 700, 500)
        
        layout = QVBoxLayout(self)
        
        # --- Info chung ---
        info_frame = QFrame()
        info_frame.setObjectName("InfoFrame")
        info_layout = QHBoxLayout(info_frame)
        
        info_text = QLabel(f"📁 {folder.name}")
        info_text.setObjectName("InfoTitle")
        info_layout.addWidget(info_text)
        
        copy_btn = QPushButton("Copy Path")
        copy_btn.setFixedWidth(100)
        copy_btn.clicked.connect(self._copy_path)
        info_layout.addStretch(1)
        info_layout.addWidget(copy_btn)
        
        layout.addWidget(info_frame)
        
        # --- Tab widget ---
        tabs = QTabWidget()
        
        # Tab 1: Original
        original_tab = QWidget()
        original_layout = QVBoxLayout(original_tab)
        original_dir = self.folder / "original"
        original_layout.addWidget(self._create_files_list(original_dir))
        tabs.addTab(original_tab, "Original")
        
        # Tab 2: Processed
        processed_tab = QWidget()
        processed_layout = QVBoxLayout(processed_tab)
        processed_dir = self.folder / "processed"
        processed_layout.addWidget(self._create_files_list(processed_dir))
        tabs.addTab(processed_tab, "Processed")
        
        # Tab 3: Text
        text_tab = QWidget()
        text_layout = QVBoxLayout(text_tab)
        text_dir = self.folder / "text"
        text_list = self._create_files_list(text_dir)
        text_layout.addWidget(text_list)
        
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setMaximumHeight(200)
        text_layout.addWidget(QLabel("Preview:"))
        text_layout.addWidget(self.text_preview)
        
        tabs.addTab(text_tab, "Text/Markdown")
        
        layout.addWidget(tabs)
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        open_btn = QPushButton("Open in Explorer")
        open_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(open_btn)
        
        delete_btn = QPushButton("Delete Folder")
        delete_btn.setObjectName("DeleteBtn")
        delete_btn.clicked.connect(self._delete_folder)
        btn_layout.addWidget(delete_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_files_list(self, directory: Path) -> QListWidget:
        """Tạo danh sách file"""
        list_widget = QListWidget()
        list_widget.setObjectName("FilesList")
        
        if not directory.exists():
            item = QListWidgetItem("(Empty)")
            item.setForeground(QColor("#999"))
            list_widget.addItem(item)
            return list_widget
        
        for file in sorted(directory.glob("*")):
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                size_text = f"{size_kb/1024:.2f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
                
                item_text = f"{file.name} ({size_text})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, str(file))
                list_widget.addItem(item)
        
        return list_widget
    
    def _copy_path(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(str(self.folder))
        QMessageBox.information(self, "Copied", "Path copied to clipboard!")
    
    def _open_folder(self):
        import os, platform
        try:
            if platform.system() == "Windows":
                os.startfile(self.folder)
            elif platform.system() == "Darwin":
                os.system(f"open '{self.folder}'")
            else:
                os.system(f"xdg-open '{self.folder}'")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open folder:\n{e}")
    
    def _delete_folder(self):
        reply = QMessageBox.question(
            self,
            'Delete Folder',
            f'Are you sure you want to delete "{self.folder.name}" and all its contents?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                import shutil
                shutil.rmtree(self.folder)
                QMessageBox.information(self, "Deleted", "Folder deleted successfully!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete:\n{e}")


class FileLogPage(BasePage):
    """
    Trang hiển thị lịch sử các file đã xử lý
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("File Log", theme_manager, parent)
        layout = self.layout()
        
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.output_dir = self.project_root / "data" / "output"
        self.theme_data = theme_manager.get_theme_data()

        # --- Search & Filter ---
        search_layout = QHBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("Search files, content...")
        self.search_bar.textChanged.connect(self._on_search)
        
        icon_path = self.project_root / "assets" / "icon" / "search.svg"
        if icon_path.exists():
            search_icon = load_svg_colored(icon_path, self.theme_data["color"]["text"]["placeholder"], 16)
            action = QAction(search_icon, "", self.search_bar)
            self.search_bar.addAction(action, QLineEdit.LeadingPosition)
        
        search_layout.addWidget(self.search_bar)
        
        # --- Sort dropdown ---
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Date (Newest)", "Date (Oldest)", "Name (A-Z)", "Name (Z-A)", "Size (Large)"])
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        search_layout.addWidget(sort_label)
        search_layout.addWidget(self.sort_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("RefreshButton")
        refresh_btn.clicked.connect(self.load_logs)
        refresh_btn.setFixedWidth(80)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)

        # --- Stats ---
        self.stats_label = QLabel()
        self.stats_label.setObjectName("StatsLabel")
        layout.addWidget(self.stats_label)

        # --- Table ---
        self.table = QTableWidget()
        self.table.setObjectName("LogTable")
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "File Name", "Size", "Processed Time", 
            "Status", "Files", "Actions"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)

        self.load_logs()

    def load_logs(self):
        self.table.setRowCount(0)
        
        if not self.output_dir.exists():
            self.stats_label.setText("No output directory found")
            return
        
        folders = [d for d in self.output_dir.iterdir() if d.is_dir()]
        total = len(folders)
        success = 0
        
        for folder in folders:
            text_dir = folder / "text"
            processed_dir = folder / "processed"
            original_dir = folder / "original"
            
            has_original = original_dir.exists() and any(original_dir.glob("*"))
            has_text = text_dir.exists() and any(text_dir.glob("*.md"))
            has_processed = processed_dir.exists() and any(processed_dir.glob("*.png"))
            
            if has_text and has_processed and has_original:
                success += 1
                status = "Success"
                status_color = "#4CAF50"
            elif has_processed:
                status = "Partial"
                status_color = "#FF9800"
            else:
                status = "Pending"
                status_color = "#2196F3"
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # File name
            self.table.setItem(row, 0, QTableWidgetItem(folder.name))
            
            # Size
            try:
                total_size = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
                size_mb = total_size / (1024 * 1024)
                size_text = f"{size_mb:.2f} MB"
            except:
                size_text = "--"
            self.table.setItem(row, 1, QTableWidgetItem(size_text))
            
            # Time
            try:
                mtime = folder.stat().st_mtime
                time_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            except:
                time_str = "--"
            self.table.setItem(row, 2, QTableWidgetItem(time_str))
            
            # Status
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(status_color))
            self.table.setItem(row, 3, status_item)
            
            # Files count
            count_text = f"O:{1 if has_original else 0} P:{1 if has_processed else 0} T:{1 if has_text else 0}"
            self.table.setItem(row, 4, QTableWidgetItem(count_text))
            
            # Actions
            view_btn = QPushButton("View")
            view_btn.setObjectName("ViewButton")
            view_btn.setFixedWidth(70)
            view_btn.clicked.connect(lambda checked, f=folder: self._view_details(f))
            self.table.setCellWidget(row, 5, view_btn)
        
        self.stats_label.setText(f"Total: {total} | ✅ Success: {success} | ❌ Failed: {total - success}")

    def _on_search(self, text: str):
        text = text.lower().strip()
        
        for row in range(self.table.rowCount()):
            filename = self.table.item(row, 0).text().lower()
            visible = not text or text in filename
            self.table.setRowHidden(row, not visible)

    def _on_sort_changed(self, sort_type: str):
        """Sắp xếp bảng"""
        rows = []
        for row in range(self.table.rowCount()):
            if not self.table.isRowHidden(row):
                rows.append(row)
        
        # Simple sort (có thể mở rộng)
        if "Name (A-Z)" in sort_type:
            rows.sort(key=lambda r: self.table.item(r, 0).text())
        elif "Name (Z-A)" in sort_type:
            rows.sort(key=lambda r: self.table.item(r, 0).text(), reverse=True)
        
        # Refresh hiển thị (có thể tối ưu hơn)
        self.load_logs()

    def _view_details(self, folder: Path):
        dialog = FileDetailDialog(folder, self.theme_data, self)
        if dialog.exec() == QDialog.Accepted:
            # Refresh nếu folder bị xóa
            self.load_logs()
```

## `home_page.py`
**Path:** `ocr_medical/ui/pages/home_page.py`

```python
from __future__ import annotations
from PySide6.QtWidgets import (QHBoxLayout, QVBoxLayout, QLineEdit, QSizePolicy,
                               QPushButton, QLabel, QFrame, QFileDialog, QWidget,
                               QScrollArea, QMessageBox, QGridLayout)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize, Signal
from pathlib import Path
from threading import Lock
import os
import logging

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

        default_output = self.project_root / "data" / "output"
        try:
            default_output.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create default output directory: {e}")

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
        """Choose storage directory"""
        folder = QFileDialog.getExistingDirectory(self, "Select storage directory")
        if folder:
            try:
                storage_path = Path(folder)
                storage_path.mkdir(parents=True, exist_ok=True)
                self.storage_path.setText(folder)
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
from PySide6.QtWidgets import QVBoxLayout, QLabel, QComboBox
from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager


class SettingPage(BasePage):
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Settings", theme_manager, parent)

        # --- Thêm combobox đổi theme ---
        layout: QVBoxLayout = self.layout()
        label = QLabel("Theme:")
        layout.addWidget(label)

        combo = QComboBox()
        combo.addItems(["light", "dark"])
        combo.setCurrentText(theme_manager.get_theme_name())
        combo.currentTextChanged.connect(theme_manager.set_theme)
        layout.addWidget(combo)

        # Nằm chân trang
        layout.addStretch(1)

```

## `dialogs.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/dialogs.qss.tpl`

```css

```

## `extract_info_page.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/extract_info_page.qss.tpl`

```css
/* ============================================================
   Extract Info Page – Light theme polished version
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
    background: #ffffff;
    padding: 60px;
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
#FileListFrame {
    border: none;
    background: transparent;
}

/* --- Header row --- */
#FileListHeader {
    background: {{ color.state.secondary.hover }};
    border: 1px solid {{ color.border.default }};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: none;

    font-weight: 600;
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}

/* --- File rows --- */
#FileListContainer {
    background: transparent;
    border: none;
}

#FileRowItem {
    border: none;
    border-bottom: 1px solid #E5E7EB;
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}

#FileRowItem:last-child {
    border-bottom: none;
}

#FileRowItem:hover {
    background: {{ color.state.secondary.hover }};
}

/* --- Status text --- */
#FileRowItem QLabel {
    font-size: 13px;
}

/* ============================================================
   TAB SECTION
   ============================================================ */
#TabContainer {
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    background: #ffffff;
    padding: 0;
}

#TabButton {
    font-weight: 600;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    border: none;
    border-bottom: 2px solid transparent;
    background: transparent;
    padding: 8px;
}
#TabButton:hover {
    background: {{ color.state.secondary.hover }};
}
#TabButton:checked {
    color: {{ color.text.secondary }};
    border-bottom: 2px solid {{ color.text.secondary }};
}

/* --- Result area --- */
#ResultBox {
    border: none;
    background: transparent;
    padding: 60px;
    color: {{ color.text.muted }};
    text-align: center;
}

/* ============================================================
   BUTTONS
   ============================================================ */
#MoreButton {
    border: none;
    background: transparent;
}
#MoreButton:hover {
    background: {{ color.state.secondary.hover }};
    border-radius: 6px;
}

#FooterButton, #FooterStopButton, #FooterSaveButton {
    min-height: 32px;
    min-width: 110px;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
    padding: 4px 10px;
}

#FooterButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.secondary }};
    background: #ffffff;
}
#FooterButton:hover {
    background: {{ color.state.secondary.hover }};
}

#FooterStopButton {
    border: none;
    color: #ffffff;
    background: #C1C1C1;
}
#FooterStopButton:hover {
    background: #AFAFAF;
}

#FooterSaveButton {
    border: none;
    color: #fff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C7BE5, stop:1 #175CD3);
}
#FooterSaveButton:hover {
    background: #357ABD;
}

```

## `file_log_page.qss.tpl`
**Path:** `ocr_medical/ui/style/pages/file_log_page.qss.tpl`

```css
/* File Log Page CSS */

#SearchBar {
    padding: 6px 10px;
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
}

#SearchBar:focus {
    border: 1px solid {{ color.state.primary.focus }};
    outline: none;
}

#RefreshButton {
    padding: 6px 12px;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.panel }};
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#RefreshButton:hover {
    background: {{ color.state.secondary.hover }};
}

#StatsLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.muted }};
    padding: 8px 0;
}

#LogTable {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: {{ color.background.panel }};
    gridline-color: {{ color.border.default }};
}

#LogTable::item {
    padding: 8px;
}

#LogTable::item:selected {
    background: {{ color.state.secondary.active }};
}

#ViewButton {
    padding: 4px 12px;
    border: 1px solid {{ color.border.default }};
    border-radius: 4px;
    background: {{ color.background.panel }};
    font-size: {{ typography.normal.size }}px;
}

#ViewButton:hover {
    background: {{ color.state.secondary.hover }};
}

#InfoFrame {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 12px;
    background: {{ color.background.panel }};
}

#InfoTitle {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
}

#FilesList {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.base }};
}

#DeleteBtn {
    background: #F44336;
    color: #ffffff;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
}

#DeleteBtn:hover {
    background: #D32F2F;
}

#InfoTabs {
    background: {{ color.background.panel }};
}

#ExtractedInfoBox, #RawInfoBox {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 10px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
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
        if icon_path.exists():
            self.btn.setIcon(load_svg_colored(
                icon_path, self.normal_color, 20))
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
            self.btn.setIcon(load_svg_colored(
                self.icon_path, self.hover_color, 20))
        QPushButton.enterEvent(self.btn, event)

    def _on_leave(self, event):
        """Trả lại màu icon khi rời hover"""
        if self.icon_path.exists() and not self.btn.isChecked():
            self.btn.setIcon(load_svg_colored(
                self.icon_path, self.normal_color, 20))
        QPushButton.leaveEvent(self.btn, event)


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
        logo_path = project_root / "assets" / "logo" / "logo-text.png"
        logo_label = QLabel()
        logo_pixmap = QPixmap(str(logo_path))
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaledToWidth(
                100, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(logo_label)

        layout.addItem(QSpacerItem(
            0, 60, QSizePolicy.Minimum, QSizePolicy.Fixed))

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
            icon_path = project_root / "assets" / "icon" / icon_file
            nav_btn = NavButton(key, text, icon_path, theme_data)
            nav_btn.btn.clicked.connect(
                lambda checked, k=key: self.page_selected.emit(k))

            layout.addWidget(nav_btn.widget())
            self.buttons[key] = nav_btn

        layout.addStretch(1)

        # --- User info at bottom ---
        user_icon_path = project_root / "assets" / "icon" / "user.svg"
        user_icon_label = QLabel()
        if user_icon_path.exists():
            user_icon_label.setPixmap(
                load_svg_colored(
                    user_icon_path, theme_data["color"]["text"]["primary"], 24).pixmap(24, 24)
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
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QStackedWidget, QFrame

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
        extract_page.navigate_back_requested.connect(lambda: self.navigate_to("home"))
        self._add_page("extra_info", extract_page)
        
        self._add_page("review", ReviewPage(self.theme_manager))

        self.side_panel.page_selected.connect(self.navigate_to)

        self.navigate_to("home")

        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name()
        )
        self.disable_focus_policy()
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
from PIL import Image
from ocr_medical.core.waifu2x_loader import load_waifu2x
from ocr_medical.core.process_image import process_image
from ocr_medical.core.ocr_extract import call_qwen_ocr
from ocr_medical.core.status import status_manager

# Output mặc định: OCR-Medical/data/output/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "output"   # 📌 sửa lại đường dẫn để nằm trong data/output

# 📌 Prompt mặc định
DEFAULT_PROMPT = (
    "Hãy trích xuất toàn bộ dữ liệu bảng trong ảnh và trình bày lại dưới dạng bảng Markdown. "
    "Yêu cầu định dạng rõ ràng như sau:\n"
    "- Hàng tiêu đề in đậm.\n"
    "- Các cột căn chỉnh bằng dấu | với khoảng trắng đều.\n"
    "- Các mục quan trọng (ví dụ MIỄN DỊCH, PXN VI SINH) phải in đậm.\n"
    "- Giữ nguyên ký hiệu đặc biệt (ví dụ dấu * phải hiển thị là \\*).\n"
    "- Giá trị số giữ nguyên định dạng, đơn vị hiển thị đúng như trong ảnh.\n"
    "Chỉ trả về bảng Markdown, không thêm lời giải thích."
)

def save_text(processed_path: Path, img_name: str, output_root: Path):
    """
    Gọi OCR và lưu kết quả Markdown
    """
    try:
        out_dir_text = output_root / img_name / "text"
        out_dir_text.mkdir(parents=True, exist_ok=True)

        extracted = call_qwen_ocr(str(processed_path), DEFAULT_PROMPT)
        ocr_path = out_dir_text / f"{img_name}_processed.md"
        with open(ocr_path, "w", encoding="utf-8") as f:
            f.write(extracted)

        status_manager.add("✅ Lưu OCR (text)")
    except Exception as e:
        status_manager.add(f"❌ Lỗi lưu OCR: {e}")
        raise

def process_input(input_path: str, output_root: str = None):
    """
    Pipeline OCR:
    - Input: file ảnh, folder, URL
    - Output: original, processed, text (.md)
    """
    status_manager.reset()
    output_root = Path(output_root) if output_root else DEFAULT_OUTPUT
    upscaler = load_waifu2x()

    # Nếu là URL
    if input_path.startswith(("http://", "https://")):
        response = requests.get(input_path)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img_name = Path(urlparse(input_path).path).stem
        _, proc_path = process_image(upscaler, img, img_name, output_root)
        save_text(proc_path, img_name, output_root)
        return status_manager

    p = Path(input_path)
    if p.is_file():
        img = Image.open(p).convert("RGB")
        img_name = p.stem
        _, proc_path = process_image(upscaler, img, img_name, output_root)
        save_text(proc_path, img_name, output_root)

    elif p.is_dir():
        for file in p.glob("*.*"):
            if file.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                img = Image.open(file).convert("RGB")
                img_name = file.stem
                _, proc_path = process_image(upscaler, img, img_name, output_root)
                save_text(proc_path, img_name, output_root)
    else:
        status_manager.add(f"❌ Input {input_path} không tồn tại")
        raise FileNotFoundError(f"Input {input_path} không tồn tại")

    return status_manager

```
