/* ============================================ */
/*         Extract Info Page - Enhanced        */
/* ============================================ */

/* Section Headers */
#SectionLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
    padding: 8px 0;
    margin-bottom: 8px;
}

/* Left & Right Panels */
#LeftPanel, #RightPanel {
    background: {{ color.background.panel }};
    border-radius: 12px;
    padding: 16px;
}

/* Main Splitter */
#MainSplitter {
    background: transparent;
}

#MainSplitter::handle {
    background: transparent;
    width: 12px;
}

/* ============================================ */
/*           Image Viewer                      */
/* ============================================ */

#ImageViewer {
    border: 2px solid {{ color.border.default }};
    border-radius: 12px;
    background: #2a2a2a;
    padding: 4px;
}

#IconButton {
    background: {{ color.background.panel }};
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 6px;
}

#IconButton:hover {
    background: {{ color.state.secondary.hover }};
    border: 1px solid {{ color.state.primary.hover }};
}

#IconButton:pressed {
    background: {{ color.state.secondary.active }};
}

/* ============================================ */
/*         Processing Files List               */
/* ============================================ */

#ProcessingFilesList {
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    background: {{ color.background.base }};
    padding: 4px;
}

#ProcessingFilesList QScrollBar:vertical {
    border: none;
    background: {{ color.background.base }};
    width: 10px;
    border-radius: 5px;
}

#ProcessingFilesList QScrollBar::handle:vertical {
    background: {{ color.border.default }};
    border-radius: 5px;
    min-height: 20px;
}

#ProcessingFilesList QScrollBar::handle:vertical:hover {
    background: {{ color.text.muted }};
}

#ProcessingFileItem {
    background: {{ color.background.panel }};
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    margin: 2px 0;
}

#ProcessingFileItem:hover {
    background: {{ color.state.secondary.hover }};
    border: 1px solid {{ color.state.primary.hover }};
}

#ProcessingFileName {
    font-size: {{ typography.normal.size }}px;
    font-weight: 500;
    color: {{ color.text.primary }};
}

#ProcessingFileStatus {
    font-size: {{ typography.normal.size }}px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 6px;
}

/* ============================================ */
/*         Result Display Tabs                 */
/* ============================================ */

#ResultTabs {
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    background: {{ color.background.panel }};
}

#ResultTabs::pane {
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    background: {{ color.background.panel }};
    padding: 12px;
}

#ResultTabs::tab-bar {
    alignment: left;
    background: transparent;
}

#ResultTabs QTabBar::tab {
    background: {{ color.background.base }};
    color: {{ color.text.muted }};
    border: 1px solid {{ color.border.default }};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
    font-size: {{ typography.normal.size }}px;
    font-weight: 600;
}

#ResultTabs QTabBar::tab:selected {
    background: {{ color.background.panel }};
    color: {{ color.text.secondary }};
    border-color: {{ color.border.default }};
}

#ResultTabs QTabBar::tab:hover:!selected {
    background: {{ color.state.secondary.hover }};
}

/* ============================================ */
/*         Markdown Preview & Raw              */
/* ============================================ */

#MarkdownPreview {
    border: none;
    border-radius: 8px;
    padding: 16px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.base }};
    line-height: 1.6;
}

#MarkdownRaw {
    border: none;
    border-radius: 8px;
    padding: 16px;
    font-size: 13px;
    color: {{ color.text.primary }};
    background: {{ color.background.base }};
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    line-height: 1.5;
}

#MarkdownRaw:focus, #MarkdownPreview:focus {
    border: 1px solid {{ color.state.primary.focus }};
    outline: none;
}

/* Custom scrollbar cho text editors */
#MarkdownPreview QScrollBar:vertical,
#MarkdownRaw QScrollBar:vertical {
    border: none;
    background: {{ color.background.base }};
    width: 12px;
    border-radius: 6px;
}

#MarkdownPreview QScrollBar::handle:vertical,
#MarkdownRaw QScrollBar::handle:vertical {
    background: {{ color.border.default }};
    border-radius: 6px;
    min-height: 30px;
}

#MarkdownPreview QScrollBar::handle:vertical:hover,
#MarkdownRaw QScrollBar::handle:vertical:hover {
    background: {{ color.text.muted }};
}

/* ============================================ */
/*         Status & Progress Bar               */
/* ============================================ */

#StatusLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    font-weight: 600;
    padding: 8px 12px;
    background: {{ color.background.panel }};
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    margin-top: 4px;
}

#ProcessProgress {
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    background: {{ color.background.base }};
    height: 28px;
    text-align: center;
}

#ProcessProgress::chunk {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 0,
        stop: 0 {{ color.text.secondary }},
        stop: 1 {{ color.state.primary.hover }}
    );
    border-radius: 9px;
}

#ProcessProgress:chunk:hover {
    background: {{ color.state.primary.active }};
}

/* ============================================ */
/*         Action Buttons                      */
/* ============================================ */

#BackButton {
    background: {{ color.background.panel }};
    color: {{ color.text.primary }};
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 10px 20px;
    font-size: {{ typography.normal.size }}px;
    font-weight: 600;
}

#BackButton:hover {
    background: {{ color.state.secondary.hover }};
    border: 1px solid {{ color.state.primary.hover }};
}

#BackButton:pressed {
    background: {{ color.state.secondary.active }};
}

#CancelButton {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #F44336,
        stop: 1 #D32F2F
    );
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: {{ typography.normal.size }}px;
    font-weight: 700;
}

#CancelButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 #E53935,
        stop: 1 #C62828
    );
}

#CancelButton:pressed {
    background: #B71C1C;
}

#CancelButton:disabled {
    background: #cccccc;
    color: #999999;
}

#SaveButton {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {{ color.text.secondary }},
        stop: 1 {{ color.state.primary.hover }}
    );
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: {{ typography.normal.size }}px;
    font-weight: 700;
}

#SaveButton:hover {
    background: qlineargradient(
        x1: 0, y1: 0, x2: 0, y2: 1,
        stop: 0 {{ color.state.primary.hover }},
        stop: 1 {{ color.state.primary.active }}
    );
}

#SaveButton:pressed {
    background: {{ color.state.primary.active }};
}

#SaveButton:disabled {
    background: #cccccc;
    color: #999999;
}

/* ============================================ */
/*         More Button & Menu                  */
/* ============================================ */

#MoreButton {
    background: {{ color.background.panel }};
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 8px;
}

#MoreButton:hover {
    background: {{ color.state.secondary.hover }};
    border: 1px solid {{ color.state.primary.hover }};
}

#MoreButton:pressed {
    background: {{ color.state.secondary.active }};
}

#MoreMenu {
    background: {{ color.background.panel }};
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    padding: 6px;
}

#MoreMenu::item {
    padding: 10px 20px;
    border-radius: 6px;
    color: {{ color.text.primary }};
    font-size: {{ typography.normal.size }}px;
}

#MoreMenu::item:selected {
    background: {{ color.state.secondary.hover }};
}

#MoreMenu::separator {
    height: 1px;
    background: {{ color.border.default }};
    margin: 6px 10px;
}

/* ============================================ */
/*         Loading Animation States            */
/* ============================================ */

#ProcessingFileItem[loading="true"] {
    animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

/* ============================================ */
/*         Responsive Adjustments              */
/* ============================================ */

#LeftPanel {
    min-width: 280px;
    max-width: 450px;
}

#RightPanel {
    min-width: 500px;
}