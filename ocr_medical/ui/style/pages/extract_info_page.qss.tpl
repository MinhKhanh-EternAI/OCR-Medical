/* ============================================================
   Extract Info Page – Light theme polished version
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
#FileListFrame {
    border: none;
    background: transparent;
}

/* --- Header row --- */
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

/* --- File rows --- */
#FileListContainer {
    background: transparent;
    border: none;
}

#FileRowItem {
    border: none;
    border-bottom: 1px solid {{ color.border.default }};
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}

#FileRowItem:last-child {
    border-bottom: none;
}

#FileRowItem:hover {
    background: {{ color.state.secondary.hover }};
}

/* --- Status text --- */
#FileRowItem QLabel {
    font-size: 13px;
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
    border: none;
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
    color: #000;
    font-size: 14px;
    text-align: left;
}

/* ============================================================
   BUTTONS (Unified size, padding, and typography)
   ============================================================ */
#MoreButton {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: transparent;
}
#MoreButton:hover {
    background: {{ color.background.base }};
}

/* --- Unified base style for all footer buttons --- */
#FooterButton, 
#FooterStopButton, 
#FooterSaveButton,
#FooterSaveAsButton {
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 700;
    border-radius: 6px;
    min-width: 110px; 
}

#FooterButton:disabled,
#FooterStopButton:disabled,
#FooterSaveButton:disabled,
#FooterSaveAsButton:disabled {
    background: #cccccc !important;
    color: #999999 !important;
    opacity: 0.7;
}

/* --- Back button --- */
#FooterButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.secondary }};
    background: transparent;
}
#FooterButton:hover {
    background: {{ color.state.secondary.hover }};
}

/* --- Stop OCR button --- */
#FooterStopButton {
    border: none;
    color: #ffffff;
    background: #FE2020;
}
#FooterStopButton:hover {
    background: #AFAFAF;
}

/* --- Save As button --- */
#FooterSaveAsButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.primary }};
    background: #ffffff;
}
#FooterSaveAsButton:hover {
    background: {{ color.state.secondary.hover }};
}

/* --- Save button --- */
#FooterSaveButton {
    border: none;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C7BE5, stop:1 #175CD3);
}
#FooterSaveButton:hover {
    background: #357ABD;
}
