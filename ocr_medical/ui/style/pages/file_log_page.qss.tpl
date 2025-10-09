/* File Log Page CSS */

#SearchBar {
    padding: 6px 10px;
    border: 1px solid {{ color.border.default }};
    border-radius: 10px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
}

#SearchBar:focus {
    border: 1px solid {{ color.state.primary.focus }};
    outline: none;
}

#RefreshButton {
    padding: 6px 12px;
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.panel }};
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#RefreshButton:hover {
    background: {{ color.state.secondary.hover }};
}

#StatsLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.muted }};
    padding: 8px 0;
}

#LogTable {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: {{ color.background.panel }};
    gridline-color: {{ color.border.default }};
}

#LogTable::item {
    padding: 8px;
}

#LogTable::item:selected {
    background: {{ color.state.secondary.active }};
}

#ViewButton {
    padding: 4px 12px;
    border: 1px solid {{ color.border.default }};
    border-radius: 4px;
    background: {{ color.background.panel }};
    font-size: {{ typography.normal.size }}px;
}

#ViewButton:hover {
    background: {{ color.state.secondary.hover }};
}

#InfoFrame {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 12px;
    background: {{ color.background.panel }};
}

#InfoTitle {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
}

#FilesList {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.base }};
}

#DeleteBtn {
    background: #F44336;
    color: #ffffff;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
}

#DeleteBtn:hover {
    background: #D32F2F;
}

#InfoTabs {
    background: {{ color.background.panel }};
}

#ExtractedInfoBox, #RawInfoBox {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 10px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
}