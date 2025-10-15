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
    background: #ffffff;
    padding: 60px;
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
    background: {{ color.state.secondary.hover }};
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
    border-bottom: 1px solid #E5E7EB;
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
    background: #ffffff;
    padding: 0;
}

#TabButton {
    font-weight: 600;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    border: none;
    border-bottom: 2px solid transparent;
    background: transparent;
    padding: 8px;
}
#TabButton:hover {
    background: {{ color.state.secondary.hover }};
}
#TabButton:checked {
    color: {{ color.text.secondary }};
    border-bottom: 2px solid {{ color.text.secondary }};
}

/* --- Result area --- */
#ResultBox {
    border: none;
    background: transparent;
    padding: 60px;
    color: {{ color.text.muted }};
    text-align: center;
}

/* ============================================================
   BUTTONS
   ============================================================ */
#MoreButton {
    border: none;
    background: transparent;
}
#MoreButton:hover {
    background: {{ color.state.secondary.hover }};
    border-radius: 6px;
}

#FooterButton, #FooterStopButton, #FooterSaveButton {
    min-height: 32px;
    min-width: 110px;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
    padding: 4px 10px;
}

#FooterButton {
    border: 1px solid {{ color.border.default }};
    color: {{ color.text.secondary }};
    background: #ffffff;
}
#FooterButton:hover {
    background: {{ color.state.secondary.hover }};
}

#FooterStopButton {
    border: none;
    color: #ffffff;
    background: #C1C1C1;
}
#FooterStopButton:hover {
    background: #AFAFAF;
}

#FooterSaveButton {
    border: none;
    color: #fff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2C7BE5, stop:1 #175CD3);
}
#FooterSaveButton:hover {
    background: #357ABD;
}
