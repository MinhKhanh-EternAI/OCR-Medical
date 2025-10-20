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
