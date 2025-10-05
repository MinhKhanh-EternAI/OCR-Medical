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
            # Cho phép chọn nhiều file
            dlg.setFileMode(QFileDialog.ExistingFiles)
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
