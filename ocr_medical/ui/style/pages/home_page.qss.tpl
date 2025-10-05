/* ****************** */
/*   Home Page CSS    */
/* ****************** */

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


/* --- Nút chức năng --- */
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

#UploadText {
    margin-top: 12px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

/* ****************** */
/*  Storage Directory */
/* ****************** */

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
    background: {{ color.text.secondary }}; /* dùng màu xanh trong theme */
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

/* ****************** */
/*   File List Row    */
/* ****************** */



#FileName {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#FileSize {
    font-size: 13px;
    color: #666;
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
    padding: 6px 10px;
}

#FileItem {
    border-top: none;
    border-left: none;
    border-right: none;
    border-bottom: 1px solid {{ color.border.default }};
}