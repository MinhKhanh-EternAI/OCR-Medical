#FileLogPage {
    background: #FFFFFF;
}

/* Top bar */
#SearchBar, #SortBox, #RefreshBtn {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 14px;
    background: #FFFFFF;
    color: {{ color.text.primary }};
    min-height: 32px;
}
#SearchBar:focus {
    border-color: {{ color.border.focus }};
    background: #FFFFFF;
}
#SortBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 24px;
    border-left: 1px solid {{ color.border.default }};
}
#SortBox:hover, #RefreshBtn:hover {
    background: {{ color.state.secondary.active }};
}

/* Folder Card */
#FolderCard {
    background: #FFFFFF;
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
}
#FolderCard:hover {
    border-color: {{ color.border.drag_area }};
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
#FolderName {
    font-weight: 700;
    color: {{ color.text.primary }};
    font-size: 15px;
}
#StatusBadge {
    color: #FFF;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    border-radius: 10px;
}

/* Buttons */
QPushButton {
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}
QPushButton#ViewBtn {
    background: {{ color.text.secondary }};
    color: #FFFFFF;
}
QPushButton#ViewBtn:hover { background: {{ color.state.primary.active }}; }
QPushButton#DeleteBtn {
    background: {{ color.border.default }};
    color: {{ color.text.primary }};
}
QPushButton#DeleteBtn:hover {
    background: {{ color.state.secondary.active }};
}
QPushButton#RefreshBtn {
    color: {{ color.text.primary }};
    background: #FFFFFF;
}

/* Pagination */
#PageBtn {
    background: #FFFFFF;
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 6px 16px;
}
#PageBtn:hover { background: {{ color.state.secondary.active }}; }
#PageLbl, #PageInfo {
    color: {{ color.text.primary }};
    font-weight: 600;
}

/* Detail Dialog */
#FileDetailDialog {
    background: #FFFFFF;
}
#LeftPanel, #RightPanel {
    background: transparent;
}
#MarkdownEditor {
    background: #FFFFFF;
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 8px;
    color: {{ color.text.primary }};
    font-family: 'Consolas';
    font-size: 14px;
}
#SaveBtn {
    background: {{ color.text.secondary }};
    color: #FFFFFF;
    border-radius: 8px;
    padding: 8px 16px;
}
#SaveBtn:hover {
    background: {{ color.state.primary.active }};
}
#ImageCompare {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: #FFFFFF;
}
