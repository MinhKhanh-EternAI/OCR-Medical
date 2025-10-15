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
