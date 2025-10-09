from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
                                QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                                QMessageBox, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QColor
from pathlib import Path
import json
from datetime import datetime

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored


class FileLogPage(BasePage):
    """
    Trang hiển thị lịch sử các file đã xử lý
    Tìm kiếm thông tin các file đã trích xuất trong data/output
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("File Log", theme_manager, parent)
        layout = self.layout()
        
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.output_dir = self.project_root / "data" / "output"
        self.theme_data = theme_manager.get_theme_data()

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
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("RefreshButton")
        refresh_btn.clicked.connect(self.load_logs)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)

        self.stats_label = QLabel()
        self.stats_label.setObjectName("StatsLabel")
        layout.addWidget(self.stats_label)

        self.table = QTableWidget()
        self.table.setObjectName("LogTable")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["File Name", "Size", "Processed Time", "Status", "Actions"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
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
            
            has_text = text_dir.exists() and any(text_dir.glob("*.md"))
            has_processed = processed_dir.exists() and any(processed_dir.glob("*.png"))
            
            if has_text and has_processed:
                success += 1
                status = "Success"
                status_color = "#4CAF50"
            elif has_processed:
                status = "Partial"
                status_color = "#FF9800"
            else:
                status = "Failed"
                status_color = "#F44336"
            
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(folder.name))
            
            try:
                total_size = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
                size_mb = total_size / (1024 * 1024)
                size_text = f"{size_mb:.2f} MB"
            except:
                size_text = "--"
            self.table.setItem(row, 1, QTableWidgetItem(size_text))
            
            try:
                mtime = folder.stat().st_mtime
                time_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = "--"
            self.table.setItem(row, 2, QTableWidgetItem(time_str))
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor(status_color))
            self.table.setItem(row, 3, status_item)
            
            view_btn = QPushButton("View")
            view_btn.setObjectName("ViewButton")
            view_btn.clicked.connect(lambda checked, f=folder: self._view_folder(f))
            self.table.setCellWidget(row, 4, view_btn)
        
        self.stats_label.setText(f"Total: {total} | Success: {success} | Failed: {total - success}")

    def _on_search(self, text: str):
        text = text.lower().strip()
        
        for row in range(self.table.rowCount()):
            filename = self.table.item(row, 0).text().lower()
            visible = not text or text in filename
            self.table.setRowHidden(row, not visible)

    def _view_folder(self, folder: Path):
        import os
        import platform
        
        try:
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":
                os.system(f"open '{folder}'")
            else:
                os.system(f"xdg-open '{folder}'")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open folder:\n{e}")