/* ============================================================
   Extract Info Page – Light theme polished version (updated)
   ============================================================ */

/* --- Layout containers --- */
#BodyContainer {
    background: transparent;
    border: none;
    padding: 0;
}

#LeftPanel, #RightPanel {
    background: transparent;
    border: none;
}

/* --- Section titles --- */
#SectionLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: 700;
    color: {{ color.text.primary }};
}

/* --- Preview box --- */
#PreviewBox {
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 12px;
}

/* ============================================================
   FILE LIST AREA
   ============================================================ */
#FileScroll {
    background: transparent;
    border-left: 1px solid {{ color.border.default }};
    border-right: 1px solid {{ color.border.default }};
    border-bottom: 1px solid {{ color.border.default }};
    border-top: none;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}

#FileListContainer {
    background: transparent;
}

#FileListHeader {
    background: {{ color.background.base }};
    border: 1px solid {{ color.border.default }};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    border-bottom: none;
    font-weight: 600;
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}
#FileRowItem {
    border-bottom: 1px solid {{ color.border.default }};
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}
#FileRowItem:hover {
    background: {{ color.state.secondary.hover }};
}

/* ============================================================
   TAB SECTION
   ============================================================ */
#TabContainer {
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 0;
}
#TabButton {
    font-weight: 600;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    border: none;
    border-bottom: 2px solid {{ color.border.default }};
    background: transparent;
    padding: 12px 6px;
}
#TabButton:hover {
    color: {{ color.text.secondary }};
    border-bottom: 2px solid {{ color.text.secondary }};
}
#TabButton:checked {
    color: {{ color.text.secondary }};
    border-bottom: 2px solid {{ color.text.secondary }};
}

/* --- Result area --- */
#ResultBox {
    border: none;
    background: transparent;
    padding: 16px;
}
QWebEngineView#ResultContent,
QTextEdit#ResultContent {
    border: none;
    background: transparent;
    outline: none;
    padding: 8px;
    color: {{ color.text.primary }};
    font-size: 15px;
    font-family: 'Segoe UI', sans-serif;
}
#EmptyStateLabel {
    font-size: 15px;
    color: {{ color.text.muted }};
    font-style: italic;
    text-align: center;
}

/* ============================================================
   LOADING TEXT
   ============================================================ */
#LoadingText {
    font-size: 32px;
    font-weight: 600;
    color: {{ color.text.secondary }};
    text-align: center;
    padding: 8px;
}

/* ============================================================
   FOOTER BUTTONS
   ============================================================ */
#FooterButton,
#FooterStopButton,
#FooterSaveButton,
#FooterSaveAsButton {
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 700;
    border-radius: 6px;
    min-width: 110px;
    transition: all 0.2s ease-in-out;
}

/* --- STOP --- */
#FooterStopButton {
    border: none;
    color: #fff;
    background: #FE2020;
}
#FooterStopButton:hover {
    background: #FF4D4D;
    transform: scale(1.03);
}

/* --- SAVE --- */
#FooterSaveButton {
    border: none;
    color: #fff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C7BE5, stop:1 #175CD3);
}
#FooterSaveButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3D8BFF, stop:1 #1A5BE8);
}

/* --- SAVE AS --- */
#FooterSaveAsButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.primary }};
    background: #fff;
}
#FooterSaveAsButton:hover {
    background: #E9F1FF;
    border: 1px solid #2C7BE5;
    color: #175CD3;
}

/* --- DEFAULT BUTTON (Back, etc.) --- */
#FooterButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.secondary }};
    background: transparent;
}
#FooterButton:hover {
    background: {{ color.state.secondary.active }};
    color: {{ color.text.secondary }};
    border-color: {{ color.state.primary.state }};
}

/* --- DISABLED STATES --- */
#FooterStopButton:disabled,
#FooterSaveButton:disabled,
#FooterSaveAsButton:disabled,
#FooterButton:disabled {
    background: #cccccc;
    color: #999999;
    box-shadow: none;
    transform: none;
}