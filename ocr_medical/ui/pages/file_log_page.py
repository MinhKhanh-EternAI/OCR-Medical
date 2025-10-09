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