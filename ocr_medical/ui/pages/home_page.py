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
                
                # Lưu vào config
                config_path = self.project_root / "config" / "app_config.json"
                config = {}
                if config_path.exists():
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                
                config["storage_dir"] = str(storage_path)
                
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
                
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