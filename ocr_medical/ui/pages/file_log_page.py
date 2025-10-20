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