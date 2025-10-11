from __future__ import annotations
from PySide6.QtWidgets import (
    QLabel, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QProgressBar, QMessageBox, QWidget, QFileDialog, QMenu,
    QTabWidget, QDialog, QFormLayout, QLineEdit,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QCheckBox
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QMutex, QMutexLocker, QSize, QPoint, QRect, QDateTime
)
from PySide6.QtGui import QPixmap, QMovie, QPainter, QColor
from pathlib import Path
from typing import Optional, Dict, List
import markdown
import math

from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager
from ocr_medical.ui.style.style_loader import load_svg_colored
from ocr_medical.core.pipeline import process_input
from ocr_medical.core.status import status_manager


# ============================================================
#                      FULLSCREEN VIEWER
# ============================================================
class FullscreenViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setBackgroundBrush(QColor("#111"))
        self._pix_item: Optional[QGraphicsPixmapItem] = None

    def set_pixmap(self, pix: QPixmap):
        self.scene.clear()
        self._pix_item = self.scene.addPixmap(pix)
        self.fitInView(self._pix_item, Qt.KeepAspectRatio)


# ============================================================
#                      PREVIEW PANEL
# ============================================================
class PreviewPanel(QWidget):
    """
    Khung preview:
      - empty: hiện icon no_image
      - loading: spinner + dòng chữ
      - ready: thông báo + nút fullscreen
    Không render ảnh inline; chỉ lưu pixmap để mở fullscreen.
    """
    def __init__(self, theme_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewContainer")
        self.theme_data = theme_data
        self._last_pixmap: Optional[QPixmap] = None
        self._on_open_fullscreen: Optional[callable] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addStretch(1)

        # --- No Image icon (QIcon -> QPixmap) ---
        self.no_img_label = QLabel(alignment=Qt.AlignCenter)
        self.no_img_label.setObjectName("NoImageLabel")
        no_icon_path = Path(__file__).resolve().parent.parent.parent / "assets" / "icon" / "no_image.svg"
        if no_icon_path.exists():
            icon = load_svg_colored(no_icon_path, "#A0A0A0", 120)
            pix = icon.pixmap(120, 120)  # convert QIcon -> QPixmap
            self.no_img_label.setPixmap(pix)
        else:
            self.no_img_label.setText("🖼 No Image")
            self.no_img_label.setStyleSheet("font-size: 20px; color: #999;")
        layout.addWidget(self.no_img_label, alignment=Qt.AlignCenter)

        # --- Spinner ---
        self.spinner = QLabel(alignment=Qt.AlignCenter)
        self.spinner.setObjectName("Spinner")
        gif_path = Path(__file__).resolve().parent.parent.parent / "assets" / "gif" / "loading.gif"
        if gif_path.exists():
            self.movie = QMovie(str(gif_path))
            self.movie.setScaledSize(QSize(64, 64))
            self.spinner.setMovie(self.movie)
        else:
            self.movie = None
            self.spinner.setText("⏳")
            self.spinner.setStyleSheet("font-size: 42px;")
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        self.spinner.hide()

        # --- Status text ---
        self.status_label = QLabel("", alignment=Qt.AlignCenter)
        self.status_label.setObjectName("SpinnerLabel")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        layout.addStretch(1)

        # --- Fullscreen button (overlay) ---
        self.full_btn = QPushButton(self)
        self.full_btn.setObjectName("FullscreenOverlay")
        self.full_btn.setCursor(Qt.PointingHandCursor)
        self.full_btn.setFixedSize(36, 36)
        fs_icon = Path(__file__).resolve().parent.parent.parent / "assets" / "icon" / "full_screen.svg"
        if fs_icon.exists():
            self.full_btn.setIcon(load_svg_colored(fs_icon, "#ffffff", 18))
            self.full_btn.setIconSize(QSize(18, 18))
        self.full_btn.setToolTip("Xem toàn màn hình")
        self.full_btn.clicked.connect(self._on_fullscreen_clicked)
        self.full_btn.hide()  # chỉ hiện khi ready

        self.setMinimumHeight(360)
        self._set_state("empty")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        margin = 10
        self.full_btn.move(self.width() - self.full_btn.width() - margin, margin)

    def _set_state(self, state: str):
        """state: empty | loading | ready"""
        self.no_img_label.setVisible(state == "empty")
        self.spinner.setVisible(state == "loading")
        self.full_btn.setVisible(state == "ready")

        if state == "loading":
            if self.movie:
                self.movie.start()
            self.status_label.setText("Đang xử lý hình ảnh...")
        elif state == "ready":
            if self.movie:
                self.movie.stop()
            self.status_label.setText("Ảnh đã sẵn sàng — nhấn để xem toàn màn hình")
        else:
            if self.movie:
                self.movie.stop()
            self.status_label.setText("")

    def _on_fullscreen_clicked(self):
        if self._on_open_fullscreen and self._last_pixmap and not self._last_pixmap.isNull():
            self._on_open_fullscreen(self._last_pixmap)

    def set_open_fullscreen_handler(self, func):
        self._on_open_fullscreen = func

    def set_loading(self, on: bool):
        self._set_state("loading" if on else "empty")

    def set_ready(self, pixmap: QPixmap):
        self._last_pixmap = pixmap
        self._set_state("ready")


# ============================================================
#                  FILE LIST (table below)
# ============================================================
class FileListTable(QTableWidget):
    COL_FILE = 0
    COL_SIZE = 1
    COL_TIME = 2
    COL_PROGRESS = 3
    COL_STATUS = 4
    COL_ACTION = 5

    def __init__(self, parent=None):
        super().__init__(0, 6, parent)
        self.setObjectName("FileListTable")
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)

        headers = ["File Name", "Size", "Processed Time", "Processed", "Status", "Action"]
        self.setHorizontalHeaderLabels(headers)
        self.setColumnWidth(self.COL_FILE, 280)
        self.setColumnWidth(self.COL_SIZE, 90)
        self.setColumnWidth(self.COL_TIME, 170)
        self.setColumnWidth(self.COL_PROGRESS, 200)
        self.setColumnWidth(self.COL_STATUS, 110)
        self.setColumnWidth(self.COL_ACTION, 70)

    @staticmethod
    def _format_size(p: Path) -> str:
        try:
            b = p.stat().st_size
        except Exception:
            return "-"
        mb = b / (1024 * 1024)
        return f"{mb:.2f} MB"

    def add_file_row(self, fpath: Path, orange_icon: Optional[Path], menu_icon: Optional[Path]) -> int:
        row = self.rowCount()
        self.insertRow(row)

        # --- File cell with icon + name
        widget = QWidget()
        h = QHBoxLayout(widget)
        h.setContentsMargins(6, 0, 0, 0)
        h.setSpacing(8)

        icon_lbl = QLabel()
        if orange_icon and orange_icon.exists():
            icon_lbl.setPixmap(load_svg_colored(orange_icon, "#FF7A00", 22).pixmap(22, 22))
        else:
            icon_lbl.setText("🧾")
        name_lbl = QLabel(fpath.name)
        name_lbl.setStyleSheet("font-weight:600;color:#333;")
        h.addWidget(icon_lbl)
        h.addWidget(name_lbl)
        h.addStretch(1)
        self.setCellWidget(row, self.COL_FILE, widget)

        # --- Size
        size_item = QTableWidgetItem(self._format_size(fpath))
        size_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, self.COL_SIZE, size_item)

        # --- Time (blank until done)
        time_item = QTableWidgetItem("")
        time_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, self.COL_TIME, time_item)

        # --- Progress
        pbar = QProgressBar()
        pbar.setObjectName("RowProgress")
        pbar.setRange(0, 100)
        pbar.setValue(0)
        pbar.setTextVisible(False)
        self.setCellWidget(row, self.COL_PROGRESS, pbar)

        # --- Status
        status_lbl = QLabel("Pending")
        status_lbl.setAlignment(Qt.AlignCenter)
        status_lbl.setStyleSheet("color:#666; font-weight:600;")
        self.setCellWidget(row, self.COL_STATUS, status_lbl)

        # --- Action (three-dot)
        btn = QPushButton()
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(32, 28)
        if menu_icon and menu_icon.exists():
            btn.setIcon(load_svg_colored(menu_icon, "#666666", 16))
        else:
            btn.setText("⋮")
        btn.setStyleSheet("border:none;")
        btn.clicked.connect(lambda: self._open_row_menu(btn, fpath))
        self.setCellWidget(row, self.COL_ACTION, btn)

        return row

    def _open_row_menu(self, btn: QPushButton, fpath: Path):
        menu = QMenu(self)
        open_dir = menu.addAction("Open containing folder")
        copy_name = menu.addAction("Copy filename")
        pos = btn.mapToGlobal(QPoint(0, btn.height()))
        action = menu.exec(pos)
        if action == open_dir:
            try:
                # best-effort open folder
                import os, platform, subprocess
                if platform.system() == "Windows":
                    os.startfile(str(fpath.parent))
                elif platform.system() == "Darwin":
                    subprocess.call(["open", str(fpath.parent)])
                else:
                    subprocess.call(["xdg-open", str(fpath.parent)])
            except Exception:
                pass
        elif action == copy_name:
            btn.window().clipboard().setText(fpath.name)

    # --- helpers to update row
    def set_row_progress(self, row: int, val: int):
        w = self.cellWidget(row, self.COL_PROGRESS)
        if isinstance(w, QProgressBar):
            w.setValue(val)

    def set_row_status(self, row: int, text: str, ok: bool | None = None):
        w = self.cellWidget(row, self.COL_STATUS)
        if isinstance(w, QLabel):
            color = "#333"
            if ok is True:
                color = "#28A745"
            elif ok is False:
                color = "#D32F2F"
            w.setText(text)
            w.setStyleSheet(f"color:{color}; font-weight:600;")

    def set_row_time_now(self, row: int):
        t = QDateTime.currentDateTime().toString("yyyy-MM-dd – HH:mm")
        item = self.item(row, self.COL_TIME)
        if item:
            item.setText(t)


# ============================================================
#                      MAIN PAGE
# ============================================================
class ExtraInfoPage(BasePage):
    navigate_back_requested = Signal()

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__("Extraction Info", theme_manager, parent)

        self.theme_manager = theme_manager
        self.theme_data = theme_manager.get_theme_data()
        self.project_root = Path(__file__).resolve().parent.parent.parent

        main_layout = self.layout()
        main_layout.setSpacing(6)

        # --- Header (title + more) ---
        main_layout.removeWidget(self.header)
        main_layout.removeWidget(self.divider)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        header.addWidget(self.header, stretch=1)

        self.more_btn = QPushButton()
        self.more_btn.setObjectName("MoreButton")
        self.more_btn.setFixedSize(32, 32)
        self.more_btn.setCursor(Qt.PointingHandCursor)
        more_icon = self.project_root / "assets" / "icon" / "more.svg"
        if more_icon.exists():
            self.more_btn.setIcon(load_svg_colored(more_icon, self.theme_data["color"]["text"]["primary"], 18))
        self.more_btn.clicked.connect(self._show_more_menu)
        header.addWidget(self.more_btn)

        main_layout.insertLayout(0, header)
        main_layout.insertWidget(1, self.divider)

        # --- Body: preview + result ---
        body = QHBoxLayout()
        body.setSpacing(10)

        # Left
        left_panel = QWidget()
        left_panel.setObjectName("LeftPanel")
        lbox = QVBoxLayout(left_panel)
        lbox.setSpacing(6)

        title1 = QLabel("File Preview")
        title1.setObjectName("SectionLabel")
        lbox.addWidget(title1)

        self.preview_panel = PreviewPanel(self.theme_data)
        self.preview_panel.set_open_fullscreen_handler(self._open_fullscreen_dialog)
        lbox.addWidget(self.preview_panel, 1)

        body.addWidget(left_panel, 4)

        # Right
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        rbox = QVBoxLayout(right_panel)
        rbox.setSpacing(6)

        title2 = QLabel("Result Display")
        title2.setObjectName("SectionLabel")
        rbox.addWidget(title2)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("ResultTabs")

        # Markdown Render Preview (read-only)
        self.preview_text = QTextEdit()
        self.preview_text.setObjectName("MarkdownPreview")
        self.preview_text.setReadOnly(True)
        self.preview_text.setHtml("<div style='color:#9aa1a9;text-align:center;'>Phần này là thông tin trích xuất</div>")
        self.tabs.addTab(self.preview_text, "Markdown Render Preview")

        # Markdown Raw Text (editable)
        self.raw_text = QTextEdit()
        self.raw_text.setObjectName("MarkdownRaw")
        self.tabs.addTab(self.raw_text, "Markdown Raw Text")

        rbox.addWidget(self.tabs, 1)
        body.addWidget(right_panel, 6)

        main_layout.addLayout(body, 1)

        # --- File list section (table) ---
        table_box = QVBoxLayout()
        table_box.setSpacing(6)

        self.file_table = FileListTable()
        table_box.addWidget(self.file_table)

        main_layout.addLayout(table_box)

        # --- Progress + Status (gộp chung box) ---
        self.status_box = QFrame()
        self.status_box.setObjectName("StatusBox")
        sb_lay = QVBoxLayout(self.status_box)
        sb_lay.setContentsMargins(8, 8, 8, 8)
        sb_lay.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProcessProgress")
        sb_lay.addWidget(self.progress_bar)

        self.status_log = QTextEdit()
        self.status_log.setObjectName("StatusLog")
        self.status_log.setReadOnly(True)
        self.status_log.setMinimumHeight(90)
        sb_lay.addWidget(self.status_log)

        main_layout.addWidget(self.status_box)

        # --- Buttons bottom ---
        btns = QHBoxLayout()
        btns.setSpacing(8)

        left_btns = QVBoxLayout()
        left_btns.setSpacing(4)

        self.back_btn = QPushButton("Back")
        self.back_btn.setObjectName("BackButton")
        back_icon = self.project_root / "assets" / "icon" / "back_page.svg"
        if back_icon.exists():
            self.back_btn.setIcon(load_svg_colored(back_icon, self.theme_data["color"]["text"]["primary"], 18))
        self.back_btn.clicked.connect(lambda: self.navigate_back_requested.emit())

        # Stop OCR toggle (disabled mặc định, bật khi đang xử lý)
        self.stop_toggle = QCheckBox("Stop OCR")
        self.stop_toggle.setEnabled(False)
        self.stop_toggle.setChecked(False)
        # style toggle đơn giản
        self.stop_toggle.setStyleSheet("""
            QCheckBox { color:#666; }
            QCheckBox::indicator { width:42px; height:22px; }
            QCheckBox::indicator:unchecked { border-radius:11px; background:#E0E0E0; }
            QCheckBox::indicator:checked { border-radius:11px; background:#FF9800; }
        """)
        self.stop_toggle.stateChanged.connect(self._on_toggle_stop)

        left_btns.addWidget(self.back_btn, 0, Qt.AlignLeft)
        left_btns.addWidget(self.stop_toggle, 0, Qt.AlignLeft)

        btns.addLayout(left_btns)

        btns.addStretch(1)

        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.setObjectName("SaveButton")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_changes)
        btns.addWidget(self.save_btn)

        main_layout.addLayout(btns)

        # Internal state
        self.thread: Optional[PipelineThread] = None
        self.current_file_path: Optional[Path] = None
        self.current_markdown: str = ""
        self.row_by_stem: Dict[str, int] = {}  # map file.stem -> row index

        # Signals
        self.raw_text.textChanged.connect(self._on_markdown_edited)
        self.file_table.itemSelectionChanged.connect(self._on_row_selected)

    # ===================== Helpers =====================
    def _open_fullscreen_dialog(self, pixmap: QPixmap):
        dlg = QDialog(self)
        dlg.setWindowTitle("Fullscreen Preview")
        dlg.setWindowFlag(Qt.FramelessWindowHint, True)
        dlg.setWindowState(Qt.WindowFullScreen)

        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(0, 0, 0, 0)
        viewer = FullscreenViewer(dlg)
        lay.addWidget(viewer)
        viewer.set_pixmap(pixmap)

        close_btn = QPushButton("✕", parent=viewer)
        close_btn.setObjectName("FullscreenOverlay")
        close_btn.setFixedSize(40, 40)
        close_btn.move(12, 12)
        close_btn.clicked.connect(dlg.close)
        dlg.exec()

    def _on_markdown_edited(self):
        md = self.raw_text.toPlainText()
        html = markdown.markdown(md, extensions=['tables', 'fenced_code'])
        if md.strip():
            self.preview_text.setHtml(html)
        else:
            self.preview_text.setHtml("<div style='color:#9aa1a9;text-align:center;'>Phần này là thông tin trích xuất</div>")

    def _append_status(self, s: str):
        self.status_log.append(s)

    def _on_toggle_stop(self, state: int):
        if state == Qt.Checked:
            self._cancel_processing()

    def _on_row_selected(self):
        row = self._selected_row()
        if row is None:
            return
        # mở xem ảnh/markdown tương ứng nếu đã tồn tại trong output
        name_item = self.file_table.cellWidget(row, FileListTable.COL_FILE)
        if not isinstance(name_item, QWidget):
            return
        name_lbl: QLabel = name_item.findChildren(QLabel)[1]  # icon + label
        fname = name_lbl.text()
        stem = Path(fname).stem

        base = Path(__file__).resolve().parent.parent.parent / "data" / "output" / stem
        processed_img = base / "processed" / f"{stem}_processed.png"
        text_md = base / "text" / f"{stem}_processed.md"

        if processed_img.exists():
            pix = QPixmap(str(processed_img))
            if not pix.isNull():
                self.preview_panel.set_ready(pix)
        else:
            self.preview_panel.set_loading(False)

        if text_md.exists():
            with open(text_md, "r", encoding="utf-8") as f:
                self.raw_text.setPlainText(f.read())
        else:
            self.raw_text.clear()
            self.preview_text.setHtml("<div style='color:#9aa1a9;text-align:center;'>Phần này là thông tin trích xuất</div>")

    def _selected_row(self) -> Optional[int]:
        sel = self.file_table.selectionModel().selectedRows()
        return sel[0].row() if sel else None

    # =================== Public API ===================
    def load_files(self, files: list[Path]):
        if not files:
            return

        if self.thread is not None and self.thread.isRunning():
            self.thread.cancel()
            self.thread.wait()

        # reset UI
        self.raw_text.clear()
        self.preview_text.setHtml("<div style='color:#9aa1a9;text-align:center;'>Phần này là thông tin trích xuất</div>")
        self.progress_bar.setValue(0)
        self.status_log.clear()
        self.preview_panel.set_loading(True)
        self.stop_toggle.setEnabled(True)
        self.stop_toggle.setChecked(False)
        self.back_btn.setEnabled(False)
        self.save_btn.setEnabled(False)

        # build table rows
        self.file_table.setRowCount(0)
        self.row_by_stem.clear()
        orange_icon = self.project_root / "assets" / "icon" / "file_image.svg"
        menu_icon = self.project_root / "assets" / "icon" / "more_vertical.svg"
        for f in files:
            row = self.file_table.add_file_row(f, orange_icon, menu_icon)
            self.row_by_stem[f.stem] = row
        if files:
            self.file_table.selectRow(0)

        # start pipeline
        self.thread = PipelineThread(files)
        self.thread.total_progress.connect(self.progress_bar.setValue)
        self.thread.status_changed.connect(self._append_status)
        self.thread.image_processed.connect(self._on_image_processed)
        self.thread.info_extracted.connect(self._display_info)
        self.thread.row_progress.connect(self._on_row_progress)
        self.thread.row_finished.connect(self._on_row_finished)
        self.thread.finished.connect(self._on_finished)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    # ================== Pipeline slots =================
    def _on_image_processed(self, image_path: Path):
        self.current_file_path = image_path.parent.parent
        pix = QPixmap(str(image_path))
        if not pix.isNull():
            self.preview_panel.set_ready(pix)

    def _display_info(self, info: str):
        self.current_markdown = info
        self.raw_text.setPlainText(info)  # triggers preview update via _on_markdown_edited

    def _on_row_progress(self, stem: str, val: int):
        row = self.row_by_stem.get(stem)
        if row is not None:
            self.file_table.set_row_progress(row, val)
            if val < 100:
                self.file_table.set_row_status(row, "Processing...", None)

    def _on_row_finished(self, stem: str, ok: bool):
        row = self.row_by_stem.get(stem)
        if row is None:
            return
        self.file_table.set_row_progress(row, 100 if ok else 0)
        self.file_table.set_row_status(row, "Success" if ok else "Error", ok)
        self.file_table.set_row_time_now(row)

    def _on_finished(self):
        self.progress_bar.setValue(100)
        self._append_status("✅ All files processed successfully")
        self.stop_toggle.setEnabled(False)
        self.back_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        # Nếu không có ảnh → về trạng thái empty
        if self.preview_panel._last_pixmap is None:
            self.preview_panel.set_loading(False)

    # =================== Menu & Actions ===================
    def _show_more_menu(self):
        # Menu đơn giản + căn đúng vị trí
        menu = QMenu(self)
        menu.setObjectName("MoreMenu")
        menu.setStyleSheet("""
            QMenu {
                background: #ffffff;
                border: 1px solid #d9d9d9;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item { padding: 6px 14px; color: #333; }
            QMenu::item:selected { background: #f2f2f2; }
        """)

        saveas = menu.addAction("💾 Save As")
        saveas.triggered.connect(self._show_save_as_dialog)
        export_md = menu.addAction("📤 Export as Markdown (.md)")
        export_md.triggered.connect(self._export_markdown)
        export_txt = menu.addAction("📤 Export as Text (.txt)")
        export_txt.triggered.connect(self._export_text)

        pos = self.more_btn.mapToGlobal(QPoint(0, self.more_btn.height()))
        menu.popup(pos)

    def _show_save_as_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Save As")
        dlg.setFixedSize(400, 120)

        form = QFormLayout(dlg)
        name = QLineEdit()
        name.setPlaceholderText("result")
        form.addRow("File name:", name)

        row = QHBoxLayout()
        ok = QPushButton("OK")
        cancel = QPushButton("Cancel")
        ok.clicked.connect(lambda: (setattr(self, '_save_name', name.text() or "result"), dlg.accept()))
        cancel.clicked.connect(dlg.reject)
        row.addStretch(1)
        row.addWidget(ok)
        row.addWidget(cancel)
        form.addRow(row)

        dlg.exec()

    def _export_markdown(self):
        if not self.raw_text.toPlainText().strip():
            QMessageBox.warning(self, "No Data", "No extracted information to export!")
            return
        filename = getattr(self, '_save_name', 'result')
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Markdown File", f"{filename}.md",
            "Markdown Files (*.md);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.raw_text.toPlainText())
                QMessageBox.information(self, "Export Successful", f"File saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save file:\n{e}")

    def _export_text(self):
        if not self.raw_text.toPlainText().strip():
            QMessageBox.warning(self, "No Data", "No extracted information to export!")
            return
        filename = getattr(self, '_save_name', 'result')
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Text File", f"{filename}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            try:
                clean = self.raw_text.toPlainText().replace('**', '').replace('|', ' ')
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(clean)
                QMessageBox.information(self, "Export Successful", f"File saved to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save file:\n{e}")

    def _save_changes(self):
        if not self.raw_text.toPlainText().strip():
            QMessageBox.warning(self, "No Changes", "No extracted information to save!")
            return
        if self.current_file_path:
            text_path = self.current_file_path / "text" / f"{self.current_file_path.name}_processed.md"
            try:
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(self.raw_text.toPlainText())
                QMessageBox.information(self, "Saved", "Changes saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save:\n{e}")

    def _cancel_processing(self):
        if self.thread and self.thread.isRunning():
            if QMessageBox.question(
                self, 'Cancel Processing', 'Hủy xử lý hiện tại?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            ) == QMessageBox.Yes:
                self.thread.cancel()
                self.stop_toggle.setEnabled(False)
                self.status_log.append("⚠️ Processing cancelled by user")
                self.preview_panel.set_loading(False)


# ============================================================
#                      PIPELINE THREAD
# ============================================================
class PipelineThread(QThread):
    total_progress = Signal(int)            # overall % for top progress bar
    status_changed = Signal(str)
    image_processed = Signal(Path)
    info_extracted = Signal(str)

    # per-row updates
    row_progress = Signal(str, int)         # stem, %
    row_finished = Signal(str, bool)        # stem, ok?

    finished = Signal()

    def __init__(self, files: list[Path]):
        super().__init__()
        self.files = files
        self._is_cancelled = False
        self._lock = QMutex()

    def cancel(self):
        with QMutexLocker(self._lock):
            self._is_cancelled = True

    def run(self):
        total = len(self.files)
        for i, file in enumerate(self.files, start=1):
            stem = file.stem
            with QMutexLocker(self._lock):
                if self._is_cancelled:
                    self.finished.emit()
                    return

            self._emit_step(f"Processing {file.name} ({i}/{total})")

            try:
                status_manager.reset()

                # simulate steps with progress per-row
                self._progress_row(stem, 5)
                self._emit_step(f"🔄 Loading image: {file.name}")
                self.msleep(200)

                self._progress_row(stem, 25)
                self._emit_step("🖼️ Enhancing image quality...")
                process_input(str(file))
                self.msleep(300)

                base = Path(__file__).resolve().parent.parent.parent
                processed_path = base / "data" / "output" / file.stem / "processed" / f"{file.stem}_processed.png"
                if processed_path.exists():
                    self._emit_step(f"✅ Image processed: {file.name}")
                    self.image_processed.emit(processed_path)
                    self._progress_row(stem, 60)

                self._emit_step("🔍 Extracting text with OCR...")
                self.msleep(300)

                text_path = base / "data" / "output" / file.stem / "text" / f"{file.stem}_processed.md"
                if text_path.exists():
                    with open(text_path, "r", encoding="utf-8") as f:
                        self.info_extracted.emit(f.read())
                    self._emit_step(f"✅ OCR completed: {file.name}")
                    self._progress_row(stem, 100)
                    self.row_finished.emit(stem, True)
                else:
                    # Still mark finished but not ok
                    self.row_finished.emit(stem, False)

            except Exception as e:
                self._emit_step(f"❌ Error processing {file.name}: {e}")
                self.row_finished.emit(stem, False)

            self.total_progress.emit(int((i / total) * 100))

        self.finished.emit()

    def _progress_row(self, stem: str, val: int):
        self.row_progress.emit(stem, max(0, min(100, val)))

    def _emit_step(self, msg: str):
        self.status_changed.emit(msg)
