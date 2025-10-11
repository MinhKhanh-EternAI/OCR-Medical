/* ============================================ */
/*         Extract Info Page - Compact          */
/* ============================================ */

/* Section Headers (giảm khoảng cách) */
#SectionLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
    padding: 2px 0;
    margin: 0 0 4px 0;
}

/* Panels (giảm padding để sát hơn) */
#LeftPanel, #RightPanel {
    background: {{ color.background.panel }};
    border-radius: 14px;
    padding: 12px;
}

/* ============================================ */
/*        File Preview (spinner + fullscreen)   */
/* ============================================ */

#PreviewContainer {
    border: 2px dashed {{ color.border.default }};
    border-radius: 14px;
    background: {{ color.background.base }};
    min-height: 360px;
    position: relative;
}

#FullscreenOverlay {
    background: rgba(0,0,0,0.35);
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    padding: 6px;
}
#FullscreenOverlay:hover {
    background: rgba(0,0,0,0.5);
    border: 1px solid {{ color.state.primary.hover }};
}
#FullscreenOverlay:pressed { background: rgba(0,0,0,0.65); }

/* Spinner + label */
#SpinnerLabel {
    color: {{ color.text.muted }};
    font-size: {{ typography.normal.size }}px;
}
#ReadyHint {
    color: {{ color.text.muted }};
    font-size: {{ typography.normal.size }}px;
}

/* ============================================ */
/*         Result Display Tabs (style ảnh 2)    */
/* ============================================ */

#ResultTabs {
    background: transparent;
    border: none;
}
#ResultTabs::pane {
    background: {{ color.background.base }};
    border: 1px solid {{ color.border.default }};
    border-radius: 16px;
    padding: 0;
    margin-top: 8px;
}

/* Tab (giống ảnh 2) */
#ResultTabs QTabBar::tab {
    background: transparent;
    color: {{ color.text.muted }};
    border: none;
    padding: 12px 22px;
    margin: 0 8px 0 0;
    font-size: {{ typography.heading3.size }}px;
    font-weight: 700;
}
#ResultTabs QTabBar::tab:selected {
    color: {{ color.state.primary.hover }};
    border-bottom: 2px solid {{ color.state.primary.hover }};
}

/* Nội dung vùng hiển thị (viền bo + nền sáng) */
#MarkdownPreview, #MarkdownRaw {
    border: none;
    border-radius: 16px;
    padding: 18px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.base }};
    line-height: 1.6;
}

/* Raw dùng mono font */
#MarkdownRaw {
    font-size: 13px;
    font-family: 'Consolas','Monaco','Courier New',monospace;
}

/* Scrollbars */
#MarkdownPreview QScrollBar:vertical,
#MarkdownRaw QScrollBar:vertical {
    border: none; background: {{ color.background.base }};
    width: 12px; border-radius: 6px;
}
#MarkdownPreview QScrollBar::handle:vertical,
#MarkdownRaw QScrollBar::handle:vertical {
    background: {{ color.border.default }};
    border-radius: 6px; min-height: 30px;
}
#MarkdownPreview QScrollBar::handle:vertical:hover,
#MarkdownRaw QScrollBar::handle:vertical:hover {
    background: {{ color.text.muted }};
}

/* ============================================ */
/*         Progress + Buttons + Status          */
/* ============================================ */

#ProcessProgress {
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    background: {{ color.background.base }};
    height: 26px;
    text-align: center;
    margin-top: 6px;
}
#ProcessProgress::chunk {
    background: qlineargradient(
        x1:0,y1:0,x2:1,y2:0,
        stop:0 {{ color.text.secondary }},
        stop:1 {{ color.state.primary.hover }}
    );
    border-radius: 9px;
}

/* Buttons */
#BackButton {
    background: {{ color.background.panel }};
    color: {{ color.text.primary }};
    border: 1px solid {{ color.border.default }};
    border-radius: 8px; padding: 8px 16px;
    font-size: {{ typography.normal.size }}px; font-weight: 600;
}
#BackButton:hover { background: {{ color.state.secondary.hover }}; border: 1px solid {{ color.state.primary.hover }}; }
#BackButton:pressed { background: {{ color.state.secondary.active }}; }

#CancelButton {
    background: qlineargradient( x1:0,y1:0,x2:0,y2:1, stop:0 #F44336, stop:1 #D32F2F );
    color: #fff; border: none; border-radius: 8px; padding: 8px 16px;
    font-size: {{ typography.normal.size }}px; font-weight: 700;
}
#CancelButton:hover { background: qlineargradient( x1:0,y1:0,x2:0,y2:1, stop:0 #E53935, stop:1 #C62828 ); }
#CancelButton:pressed { background: #B71C1C; }
#CancelButton:disabled { background: #cccccc; color: #999999; }

#SaveButton {
    background: qlineargradient( x1:0,y1:0,x2:0,y2:1, stop:0 {{ color.text.secondary }}, stop:1 {{ color.state.primary.hover }} );
    color:#fff;border:none;border-radius:8px;padding:8px 18px;
    font-size: {{ typography.normal.size }}px; font-weight: 700;
}
#SaveButton:hover {
    background: qlineargradient( x1:0,y1:0,x2:0,y2:1, stop:0 {{ color.state.primary.hover }}, stop:1 {{ color.state.primary.active }} );
}
#SaveButton:pressed { background: {{ color.state.primary.active }}; }
#SaveButton:disabled { background:#ccc;color:#999; }

/* Status log (dưới cùng) */
#StatusLog {
    border: 1px dashed {{ color.border.default }};
    border-radius: 10px;
    background: {{ color.background.base }};
    padding: 8px;
    font-size: 12px;
    color: {{ color.text.primary }};
    margin-top: 6px;
}

/* Responsive width */
#LeftPanel { min-width: 320px; max-width: 500px; }
#RightPanel { min-width: 520px; }
