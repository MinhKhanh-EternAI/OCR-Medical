# Cấu trúc dự án
```bash
OCR-Medical/
│
├─ ocr_medical/
│  ├─ __init__.py
│  ├─ main.py
│  ├─ watch.py
│  ├─ requirements.txt
│  │
│  ├─ assets/
│  │  ├─ fonts/
│  │  ├─ icon/
│  │  └─ logo/
│  │
│  ├─ config/
│  │  ├─ app_config.json
│  │  └─ __init__.py
│  │
│  ├─ core/
│  │  ├─ ocr_extract.py
│  │  ├─ pipeline.py
│  │  ├─ process_image.py
│  │  ├─ status.py
│  │  ├─ waifu2x_loader.py
│  │  └─ __init__.py
│  │
│  ├─ data/
│  │  ├─ output/
│  │  │  ├─ test_01/
│  │  │  │  ├─ original/
│  │  │  │  ├─ processed/
│  │  │  │  └─ text/
│  │  │  ├─ ...
│  │  └─ samples/
│  │
│  ├─ ui/
│  │  ├─ __init__.py
│  │  ├─ main_window.py
│  │  │
│  │  ├─ pages/
│  │  │  ├─ __init__.py
│  │  │  ├─ base_page.py
│  │  │  ├─ extract_info_page.py
│  │  │  ├─ file_log_page.py
│  │  │  ├─ home_page.py
│  │  │  ├─ review_page.py
│  │  │  └─ setting_page.py
│  │  │
│  │  ├─ style/
│  │  │  ├─ __init__.py
│  │  │  ├─ style_loader.py
│  │  │  ├─ theme_manager.py
│  │  │  │
│  │  │  ├─ pages/
│  │  │  │  ├─ style.qss.tpl
│  │  │  │  ├─ home_page.qss.tpl
│  │  │  │  ├─ extract_info_page.qss.tpl
│  │  │  │  ├─ file_log_page.qss.tpl
│  │  │  │  ├─ review_page.qss.tpl
│  │  │  │  └─ setting_page.qss.tpl
│  │  │  │
│  │  │  └─ theme/
│  │  │     ├─ theme_dark.json
│  │  │     └─ theme_light.json
│  │  │
│  │  └─ widgets/
│  │     ├─ __init__.py
│  │     └─ side_panel.py
│  │
│  ├─ utils/
│  │  ├─ helpers.py
│  │  ├─ logger.py
│  │  └─ __init__.py
│  │
│  └─ config/
│     ├─ app_config.json
│     └─ __init__.py
│
├─ Requirement/
│  └─ Kickoff N6-BData.pdf
│
├─ prompt.md
└─ README.md                                                          

```

# Code của các file giao diện
## A. Pages
### 1. Base page: ocr_medical\ui\pages\base_page.py
```bash
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


### 2. Extracr Info Page: ocr_medical\ui\pages\extract_info_page.py
```bash
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
```

### 3. File Log page: ocr_medical\ui\pages\file_log_page.py
```bash
from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager

class FileLogPage(BasePage):
    """
    Trang hiển thị lịch sử các file đã xử lý.
    TODO: Thêm table/list view để hiển thị file log.
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("File Log", theme_manager, parent)
        layout = self.layout()

        # TODO: Thêm widget hiển thị danh sách file log
        
        layout.addStretch(1)
```

### 4. Home page: ocr_medical\ui\pages\home_page.py
```bash
from __future__ import annotations
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QSizePolicy, QPushButton, QLabel, QFrame, QFileDialog, QWidget, QScrollArea
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize, Signal
from pathlib import Path
import os

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored


class FileItem(QFrame):
    """
    Widget hiển thị thông tin của 1 file trong danh sách.
    Bao gồm: icon, tên file, kích thước, nút xóa.
    """
    def __init__(self, file_path: Path, theme_data: dict, project_root: Path,
                 remove_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("FileItem")

        self.file_path = Path(file_path)
        self.remove_callback = remove_callback
        self.theme_data = theme_data
        self.project_root = project_root

        # Layout ngang với spacing đều
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(12)

        # --- Icon file ---
        file_icon_path = project_root / "assets" / "icon" / "file.svg"
        icon_label = QLabel()
        if file_icon_path.exists():
            icon = load_svg_colored(file_icon_path, "#1A73E8", 20)
            icon_label.setPixmap(icon.pixmap(QSize(20, 20)))
        icon_label.setFixedSize(28, 28)
        icon_label.setObjectName("FileIcon")
        layout.addWidget(icon_label)

        # --- Tên file (co giãn để lấp đầy không gian) ---
        self.name_label = QLabel(self.file_path.name)
        self.name_label.setObjectName("FileName")
        layout.addWidget(self.name_label, stretch=1)

        # --- Kích thước file ---
        try:
            size_kb = os.path.getsize(self.file_path) / 1024
            # Hiển thị Mb nếu > 1024 Kb, ngược lại hiển thị Kb
            size_txt = f"{size_kb/1024:.1f} Mb" if size_kb > 1024 else f"{size_kb:.0f} Kb"
        except Exception:
            size_txt = "--"
        size_label = QLabel(size_txt)
        size_label.setObjectName("FileSize")
        layout.addWidget(size_label)
        layout.addStretch(2)

        # --- Nút xóa ---
        close_icon_path = project_root / "assets" / "icon" / "close.svg"
        delete_btn = QPushButton()
        delete_btn.setObjectName("DeleteButton")
        if close_icon_path.exists():
            delete_btn.setIcon(load_svg_colored(close_icon_path, "#666", 20))
        delete_btn.setFixedSize(28, 28)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.remove_self)
        layout.addWidget(delete_btn)

    def remove_self(self):
        """Xóa widget này khỏi UI và gọi callback để cập nhật danh sách"""
        self.setParent(None)
        self.deleteLater()
        self.remove_callback(self.file_path)


class DropArea(QFrame):
    """
    Khung upload hỗ trợ 2 cách:
    1. Click chuột để mở file dialog
    2. Kéo-thả file vào khung
    """
    def __init__(self, on_files_selected, parent=None):
        super().__init__(parent)
        self.on_files_selected = on_files_selected
        self.setAcceptDrops(True)  # Bật chế độ nhận drag & drop
        self.setObjectName("UploadBox")

    def mousePressEvent(self, event):
        """Xử lý sự kiện click chuột - mở file dialog"""
        if event.button() == Qt.LeftButton:
            dlg = QFileDialog(self, "Select files")
            dlg.setFileMode(QFileDialog.ExistingFiles)  # Cho phép chọn nhiều file
            dlg.setNameFilter(
                "Images (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff)")
            if dlg.exec():
                paths = [Path(p) for p in dlg.selectedFiles()]
                self.on_files_selected(paths)
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        """Kiểm tra xem file được kéo vào có hợp lệ không"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Xử lý khi thả file vào"""
        urls = event.mimeData().urls()
        paths = [Path(u.toLocalFile()) for u in urls if u.isLocalFile()]
        if paths:
            self.on_files_selected(paths)
        event.acceptProposedAction()


class HomePage(BasePage):
    """
    Trang chủ - nơi người dùng upload và quản lý file đầu vào.
    Tính năng:
    - Upload file (click hoặc drag & drop)
    - Scan từ folder
    - Hiển thị danh sách file
    - Chọn thư mục output
    - Gửi file đi xử lý
    """
    # Signal phát ra khi người dùng nhấn "Process Document"
    process_requested = Signal(list)

    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("OCR - Medical", theme_manager, parent)

        # Lưu thông tin cần thiết
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.theme_data = theme_manager.get_theme_data()
        self.files: list[Path] = []  # Danh sách file đã chọn

        layout = self.layout()

        # ========== Header + Search Bar ==========
        header_layout = QHBoxLayout()
        # Di chuyển header từ BasePage vào layout ngang
        layout.removeWidget(self.header)
        header_layout.addWidget(self.header)

        # Thanh search với icon
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("Search files, patients IDs...")
        self.search_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.search_bar.setMinimumWidth(200)
        self.search_bar.setMaximumWidth(800)

        # Thêm icon search vào search bar
        icon_path = self.project_root / "assets" / "icon" / "search.svg"
        icon_color = self.theme_data["color"]["text"]["placeholder"]
        if icon_path.exists():
            search_icon = load_svg_colored(icon_path, icon_color, 16)
            action = QAction(search_icon, "", self.search_bar)
            self.search_bar.addAction(action, QLineEdit.LeadingPosition)

        header_layout.addWidget(self.search_bar, stretch=1)
        layout.insertLayout(0, header_layout)

        # ========== Action Buttons (3 nút chính) ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        # Danh sách các nút action với (text, icon, handler)
        actions = [
            ("Scan from Folder", "folder_plus.svg", self.scan_from_folder),
            ("Capture with Camera", "camera.svg", self._todo),
            ("Fetch from URL", "link.svg", self._todo),
        ]

        for text, icon_file, handler in actions:
            btn = QPushButton("  " + text)
            btn.setObjectName("ActionButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setFocusPolicy(Qt.NoFocus)

            # Load icon SVG với màu từ theme
            ip = self.project_root / "assets" / "icon" / icon_file
            if ip.exists():
                btn.setIcon(load_svg_colored(
                    ip, self.theme_data["color"]["text"]["primary"], 18))
                btn.setIconSize(QSize(18, 18))

            btn.clicked.connect(handler)
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)

        # ========== Upload Box (Drag & Drop + Click) ==========
        upload_box = DropArea(on_files_selected=self.add_files)
        upload_layout = QVBoxLayout(upload_box)
        upload_layout.setContentsMargins(20, 20, 20, 20)
        upload_layout.setSpacing(8)
        upload_layout.setAlignment(Qt.AlignCenter)

        # Icon upload
        upload_icon_path = self.project_root / "assets" / "icon" / "upload.svg"
        if upload_icon_path.exists():
            upload_icon = load_svg_colored(
                upload_icon_path, self.theme_data["color"]["text"]["primary"], 48)
            icon_label = QLabel()
            icon_label.setPixmap(upload_icon.pixmap(QSize(48, 48)))
            icon_label.setAlignment(Qt.AlignCenter)
            upload_layout.addWidget(icon_label)

        # Text hướng dẫn
        upload_text = QLabel(
            "Click or drag your files here to extract information")
        upload_text.setObjectName("UploadText")
        upload_text.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_text)

        layout.addWidget(upload_box)

        # ========== Storage Directory (Chọn thư mục output) ==========
        storage_frame = QFrame()
        storage_frame.setObjectName("StorageFrame")
        storage_layout = QHBoxLayout(storage_frame)
        storage_layout.setContentsMargins(0, 0, 0, 0)
        storage_layout.setSpacing(8)

        # Icon folder + label
        folder_icon_path = self.project_root / "assets" / "icon" / "folder.svg"
        folder_box = QFrame()
        folder_box.setObjectName("FolderBox")
        folder_layout = QHBoxLayout(folder_box)
        folder_layout.setContentsMargins(8, 4, 8, 4)
        folder_layout.setSpacing(6)

        if folder_icon_path.exists():
            folder_icon = load_svg_colored(
                folder_icon_path, self.theme_data["color"]["text"]["primary"], 16)
            folder_icon_label = QLabel()
            folder_icon_label.setPixmap(folder_icon.pixmap(QSize(16, 16)))
            folder_layout.addWidget(folder_icon_label)

        folder_label = QLabel("Storage Directory")
        folder_label.setObjectName("StorageLabel")
        folder_layout.addWidget(folder_label)
        storage_layout.addWidget(folder_box)

        # Đường dẫn thư mục output (read-only)
        self.storage_path = QLineEdit(
            r"C:\Users\khanhnvm\Documents\workspace\OCR-Medical\ocr_medical\data\output"
        )
        self.storage_path.setObjectName("StoragePath")
        self.storage_path.setReadOnly(True)
        storage_layout.addWidget(self.storage_path, stretch=1)

        # Nút "..." để chọn thư mục khác
        more_icon_path = self.project_root / "assets" / "icon" / "more.svg"
        self.more_btn = QPushButton()
        self.more_btn.setObjectName("MoreButton")
        self.more_btn.setCursor(Qt.PointingHandCursor)
        self.more_btn.setFixedSize(32, 32)
        if more_icon_path.exists():
            self.more_btn.setIcon(load_svg_colored(
                more_icon_path, self.theme_data["color"]["text"]["primary"], 16))
            self.more_btn.setIconSize(QSize(16, 16))
        self.more_btn.clicked.connect(self.choose_storage_dir)
        storage_layout.addWidget(self.more_btn)

        layout.addWidget(storage_frame)

        # ========== File List (Danh sách file đã chọn) ==========
        self.file_scroll = QScrollArea()
        self.file_scroll.setObjectName("FileList")
        self.file_scroll.setWidgetResizable(True)
        
        # Container chứa các FileItem
        self.file_list_container = QWidget()
        self.file_list_container.setObjectName("FileListContainer")
        self.file_list_layout = QVBoxLayout(self.file_list_container)
        self.file_list_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list_layout.setSpacing(0)
        self.file_list_layout.setAlignment(Qt.AlignTop)
        
        self.file_scroll.setWidget(self.file_list_container)
        layout.addWidget(self.file_scroll)

        # ========== Footer (Tổng số file + Nút Process) ==========
        footer_layout = QHBoxLayout()

        # Label hiển thị tổng số file
        self.total_files_label = QLabel("Total files: 0")
        self.total_files_label.setObjectName("TotalFilesLabel")
        footer_layout.addWidget(self.total_files_label)

        # Nút bắt đầu xử lý (disabled khi chưa có file)
        self.process_btn = QPushButton("Process Document")
        self.process_btn.setObjectName("ProcessButton")
        self.process_btn.setCursor(Qt.PointingHandCursor)
        self.process_btn.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.process_btn.setMinimumHeight(36)
        self.process_btn.setEnabled(False)
        footer_layout.addWidget(self.process_btn, stretch=1)

        self.process_btn.clicked.connect(self._process_files)

        layout.addLayout(footer_layout)

    # ========== Actions / Logic ==========
    
    def _todo(self):
        """Placeholder cho các tính năng chưa implement"""
        pass

    def scan_from_folder(self):
        """Mở dialog chọn folder và thêm tất cả file trong folder"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select folder to scan")
        if not folder:
            return
        p = Path(folder)
        # Lấy tất cả file (không đệ quy)
        files = [f for f in p.iterdir() if f.is_file()]
        self.add_files(files)

    def choose_storage_dir(self):
        """Cho phép người dùng chọn thư mục output khác"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select storage directory")
        if folder:
            self.storage_path.setText(folder)

    def add_files(self, paths: list[Path]):
        """
        Thêm file vào danh sách.
        Kiểm tra:
        - File tồn tại và không phải folder
        - Extension hợp lệ
        - Không trùng lặp
        """
        VALID_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff"}
        
        for p in paths:
            p = Path(p).resolve()
            
            # Kiểm tra file tồn tại và không phải folder
            if not p.exists() or p.is_dir():
                continue
            
            # Kiểm tra extension
            if p.suffix.lower() not in VALID_EXT:
                continue
            
            # Kiểm tra trùng lặp
            if any(f.resolve() == p for f in self.files):
                continue
            
            # Thêm vào danh sách
            self.files.append(p)

            # Tạo widget FileItem và thêm vào UI
            item = FileItem(
                p, self.theme_data, self.project_root,
                remove_callback=self.remove_file
            )
            self.file_list_layout.addWidget(item)
        
        self.update_total_files()

    def remove_file(self, file_path: Path):
        """Xóa file khỏi danh sách (được gọi từ FileItem)"""
        try:
            self.files.remove(file_path)
        except ValueError:
            pass
        self.update_total_files()

    def update_total_files(self):
        """Cập nhật label tổng số file và trạng thái nút Process"""
        self.total_files_label.setText(f"Total files: {len(self.files)}")
        self.process_btn.setEnabled(len(self.files) > 0)

    def _process_files(self):
        """Emit signal để MainWindow điều hướng sang trang Extract Info"""
        if not self.files:
            return
        self.process_requested.emit(self.files)

    def mousePressEvent(self, event):
        """Xóa focus khỏi search bar khi click ra ngoài"""
        if hasattr(self, "search_bar") and not self.search_bar.geometry().contains(event.pos()):
            self.search_bar.clearFocus()
        super().mousePressEvent(event)
```

### 5. Review page: ocr_medical\ui\pages\home_page.py
```bash
from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager

class ReviewPage(BasePage):
    """
    Trang review kết quả sau khi xử lý OCR.
    TODO: Thêm UI để hiển thị và chỉnh sửa kết quả.
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Review", theme_manager, parent)
        
        layout = self.layout()

        # TODO: Thêm widget hiển thị kết quả OCR
        # - Table/Form hiển thị thông tin đã trích xuất
        # - Nút chỉnh sửa
        # - Nút export
        
        # Nằm chân trang
        layout.addStretch(1)
```

### 6. Setting page: ocr_medical\ui\pages\setting_page.py
```bash
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

## B. Style
### Style loader: ocr_medical\ui\style\style_loader.py
```bash
from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer


STYLE_DIR = Path(__file__).parent
THEME_DIR = STYLE_DIR / "theme"
PAGES_DIR = STYLE_DIR / "pages"


def load_theme_qss(theme: str = "light", page: str | None = None) -> str:
    """Render QSS từ template + theme JSON."""
    theme_file = THEME_DIR / f"theme_{theme}.json"
    theme_data = json.loads(theme_file.read_text(encoding="utf-8"))

    if page:
        tpl_file = PAGES_DIR / f"{page}.qss.tpl"
    else:
        tpl_file = STYLE_DIR / "pages" / "style.qss.tpl"

    template = tpl_file.read_text(encoding="utf-8")

    def deep_format(s: str, ctx: dict, prefix="") -> str:
        out = s
        for k, v in ctx.items():
            if isinstance(v, dict):
                out = deep_format(out, v, f"{prefix}{k}.")
            else:
                out = out.replace(f"{{{{ {prefix}{k} }}}}", str(v))
        return out

    return deep_format(template, theme_data)


def load_theme_data(theme: str = "light") -> dict:
    """Load raw theme JSON (dùng trong code Python)."""
    THEME_DIR = STYLE_DIR / "theme"
    theme_file = THEME_DIR / f"theme_{theme}.json"
    return json.loads(theme_file.read_text(encoding="utf-8"))


def load_svg_colored(path: Path, color: str, size: int = 20) -> QIcon:
    """Load SVG và tô lại bằng màu theme"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    renderer = QSvgRenderer(str(path))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()

    return QIcon(pixmap)
```

### Theme manager: ocr_medical\ui\style\theme_manager.py
```bash
from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal

STYLE_DIR = Path(__file__).parent
THEME_DIR = STYLE_DIR / "theme"


class ThemeManager(QObject):
    """Quản lý theme tập trung (light/dark)."""
    theme_changed = Signal(dict, str)  # (theme_data, theme_name)

    def __init__(self, theme: str = "light") -> None:
        super().__init__()
        self._theme_name = theme
        self._theme_data = self._load_theme(theme)

    def _load_theme(self, theme: str) -> dict:
        theme_file = THEME_DIR / f"theme_{theme}.json"
        return json.loads(theme_file.read_text(encoding="utf-8"))

    def get_theme_data(self) -> dict:
        return self._theme_data

    def get_theme_name(self) -> str:
        return self._theme_name

    def set_theme(self, theme: str) -> None:
        """Đổi theme và phát signal cho toàn app."""
        if theme != self._theme_name:
            self._theme_name = theme
            self._theme_data = self._load_theme(theme)
            self.theme_changed.emit(self._theme_data, self._theme_name)
```
### ocr_medical\ui\style\pages\style.qss.tpl
```bash
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
```

### ocr_medical\ui\style\pages\home_page.qss.tpl
```bash
/* ****************** */
/*   Home Page CSS    */
/* ****************** */

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


/* --- Nút chức năng --- */
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

#UploadText {
    margin-top: 12px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

/* ****************** */
/*  Storage Directory */
/* ****************** */

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
    background: {{ color.text.secondary }}; /* dùng màu xanh trong theme */
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

/* ****************** */
/*   File List Row    */
/* ****************** */



#FileName {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#FileSize {
    font-size: 13px;
    color: #666;
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
    padding: 6px 10px;
}

#FileItem {
    border-top: none;
    border-left: none;
    border-right: none;
    border-bottom: 1px solid {{ color.border.default }};
}
```
## ocr_medical\ui\style\theme\theme_light.json
```bash
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
## Widget
### ocr_medical\ui\widgets\side_panel.py
```bash
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
## ocr_medical\ui\main_window.py
```bash
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


# ---------- Layout constants ----------
MARGIN = 24
GUTTER = 24
SIDE_COLS = 2
TOTAL_COLS = 12
MAIN_COLS = TOTAL_COLS - SIDE_COLS
TOTAL_ROWS = 12


# ---------- Panel wrapper ----------
class Panel(QFrame):
    """Khung panel có border / nền đồng nhất theo theme."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("Panel")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)


# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self, project_root: Path, theme_name: str = "light") -> None:
        super().__init__()
        self.project_root = project_root
        self.setWindowTitle("OCR-Medical")

        # --- Theme manager ---
        self.theme_manager = ThemeManager(theme_name)
        self.theme_manager.theme_changed.connect(self.apply_theme)

        # --- Central container ---
        root = QWidget(self)
        self.setObjectName("MainWindow")
        self.setCentralWidget(root)

        grid = QGridLayout(root)
        grid.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)
        grid.setHorizontalSpacing(GUTTER)
        grid.setVerticalSpacing(GUTTER)

        # Chia layout 12 cột / 12 hàng
        for c in range(TOTAL_COLS):
            grid.setColumnStretch(c, 1)
        for r in range(TOTAL_ROWS):
            grid.setRowStretch(r, 1)

        # ---------- Side Panel ----------
        self.side_panel = SidePanel(
            project_root=self.project_root,
            theme_manager=self.theme_manager
        )
        side_wrapper = Panel()
        from PySide6.QtWidgets import QGridLayout as QGL
        side_layout = QGL(side_wrapper)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.addWidget(self.side_panel, 0, 0, 1, 1)

        # ---------- Main Stack ----------
        self.stack = QStackedWidget()
        main_wrapper = Panel()
        main_layout = QGL(main_wrapper)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack, 0, 0, 1, 1)

        # Thêm vào grid
        grid.addWidget(side_wrapper, 0, 0, TOTAL_ROWS, SIDE_COLS)
        grid.addWidget(main_wrapper, 0, SIDE_COLS, TOTAL_ROWS, MAIN_COLS)

        # ---------- Pages ----------
        self.page_index: dict[str, int] = {}

        # Trang Home (có phát signal khi nhấn Process)
        home_page = HomePage(self.theme_manager)
        home_page.process_requested.connect(self._go_to_extract_info)
        self._add_page("home", home_page)

        # Các trang còn lại
        self._add_page("setting", SettingPage(self.theme_manager))
        self._add_page("file_log", FileLogPage(self.theme_manager))
        self._add_page("extra_info", ExtraInfoPage(self.theme_manager))
        self._add_page("review", ReviewPage(self.theme_manager))

        # Bắt sự kiện điều hướng từ side panel
        self.side_panel.page_selected.connect(self.navigate_to)

        # Trang mặc định
        self.navigate_to("home")

        # Áp style global lần đầu
        self.apply_theme(
            self.theme_manager.get_theme_data(),
            self.theme_manager.get_theme_name()
        )

    # ------------------------------------------------------
    def _add_page(self, key: str, widget: QWidget) -> None:
        """Thêm 1 trang vào stack widget."""
        idx = self.stack.addWidget(widget)
        self.page_index[key] = idx

    # ------------------------------------------------------
    def navigate_to(self, key: str) -> None:
        """Chuyển sang trang theo key."""
        if key in self.page_index:
            self.stack.setCurrentIndex(self.page_index[key])
            self.side_panel.set_active(key)

    # ------------------------------------------------------
    def _go_to_extract_info(self, files: list[Path]):
        """Khi nhấn Process Document ở Home."""
        self.navigate_to("extra_info")

        # Lấy trang Extract Info
        page = self.stack.widget(self.page_index["extra_info"])
        if hasattr(page, "load_files"):
            page.load_files(files)

    # ------------------------------------------------------
    def apply_theme(self, theme_data: dict, theme_name: str) -> None:
        """Áp dụng theme toàn app."""
        qss = load_theme_qss(theme_name)
        self.setStyleSheet(qss)
```

## ocr_medical\main.py
```bash
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