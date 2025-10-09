/* Extract Info Page CSS */

#SectionLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
    margin-top: 8px;
    margin-bottom: 4px;
}

#ProcessedImagePreview {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: {{ color.background.base }};
}

#ProcessingFilesList {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    background: {{ color.background.panel }};
}

#ProcessingFileItem {
    background: {{ color.background.panel }};
    border-bottom: 1px solid {{ color.border.default }};
    padding: 4px;
}

#ProcessingFileName {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#ProcessingFileStatus {
    font-size: {{ typography.normal.size }}px;
    font-weight: 600;
}

#ExtractedInfoBox {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 12px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
    font-family: 'Consolas', 'Monaco', monospace;
}

#OutputNameEdit, #OutputPathEdit {
    border: 1px solid {{ color.border.default }};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
}

#OutputPathEdit:read-only {
    background: {{ color.background.base }};
}

#CancelButton {
    background: #F44336;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: {{ typography.normal.size }}px;
}

#CancelButton:hover {
    background: #D32F2F;
}

#CancelButton:disabled {
    background: #ccc;
    color: #999;
}