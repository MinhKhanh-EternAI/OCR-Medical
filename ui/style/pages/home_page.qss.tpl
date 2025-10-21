/* Home Page CSS */

#ActionButton {
    padding: 6px 10px;
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: {{ color.background.panel }};
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#ActionButton:hover {
    background: {{ color.state.secondary.hover }};
}

#UploadBox {
    border: 2px dashed {{ color.text.secondary }};
    border-radius: 12px;
    background: {{ color.background.drag_area }};
    padding: 40px;
    margin-top: 24px;
}

#UploadBox_Dragging {
    border: 2px solid {{ color.text.secondary }};
    background: rgba(23, 92, 211, 0.1);
}

#UploadText {
    margin-top: 12px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#StorageFrame {
    margin-top: 16px;
}

#FolderBox {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.panel }};
}

#StorageLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    font-weight: 600;
}

#StoragePath {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
}

#StoragePath:read-only {
    background: {{ color.background.base }};
}

#MoreButton {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    background: {{ color.background.panel }};
    padding: 4px;
}

#MoreButton:hover {
    background: {{ color.state.secondary.hover }};
}

#TotalFilesLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#ProcessButton {
    background: {{ color.text.secondary }};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-weight: 700;
    padding: 8px 16px;
    font-size: 15px;
}

#ProcessButton:hover {
    background: {{ color.state.primary.hover }};
}

#ProcessButton:pressed {
    background: {{ color.state.primary.active }};
}

#ProcessButton:disabled {
    background: #cccccc;
    color: #999999;
}

#FileName {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#FileSize {
    font-size: 13px;
    color: #666;
}

#FileIndex {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    font-weight: 600;
}

#DeleteButton {
    border: 1px solid transparent;
    border-radius: 6px;
}

#DeleteButton:hover {
    background: {{ color.background.base }};
    border: 1px solid transparent;
    border-radius: 6px;
}

#FileList {
    border: none;
    background: {{ color.background.panel }};
}

#FileListContainer {
    background: {{ color.background.panel }};
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 0px;
}

#FileListHeader {
    background: {{ color.background.base }};
    border: 1px solid {{ color.border.default }};
    border-bottom: none;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}

#FileHeaderColumn {
    background: {{ color.background.base }};
    border-right: 1px solid {{ color.border.default }};
}

#FileHeaderColumn:last-child {
    border-right: none;
}

#FileHeaderLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    font-weight: 700;
    letter-spacing: 0.5px;
}

#FileListSeparator {
    background: {{ color.border.default }};
}

#FileItemColumn {
    background: transparent;
    border-right: 1px solid {{ color.border.default }};
}

#FileItemColumn:last-child {
    border-right: none;
}

#FileItem {
    border-bottom: 1px solid {{ color.border.default }};
}

#FileItem:last-child {
    border-bottom: none;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}