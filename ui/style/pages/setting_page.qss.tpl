/* ============================================================
   Settings Page – scoped styles
   Only apply to content inside #SettingsForm
   ============================================================ */

#SettingsForm QLabel {
    font-size: 15px;
    font-weight: 600;
    color: {{ color.text.primary }};
    margin-top: 6px;
}

#SettingsForm QLineEdit#SettingLineEdit {
    background: #fff;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 14px;
    color: {{ color.text.primary }};
}

#SettingsForm QLineEdit#SettingLineEdit:focus {
    border: 1px solid {{ color.border.focus }};
}

#SettingsForm QComboBox#SettingComboBox {
    background: #fff;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 14px;
}

#SettingsForm QComboBox#SettingComboBox::drop-down {
    width: 24px;
    border: none;
}

#SettingsForm QPushButton#BrowseButton {
    padding: 8px 16px;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: #f8f9fa;
}

#SettingsForm QPushButton#BrowseButton:hover {
    background: #e9ecef;
}

#SettingsForm QPushButton#SaveButton {
    margin-top: 16px;
    padding: 8px 16px;
    font-weight: 700;
    border-radius: 6px;
    color: #fff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C7BE5, stop:1 #175CD3);
}

#SettingsForm QPushButton#SaveButton:hover {
    background: #357ABD;
}

#SettingsForm QPushButton#SaveButton:pressed {
    background: #2C5AA0;
}
