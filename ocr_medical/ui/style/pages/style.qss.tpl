/* ****************** */
/*   1. Main Window   */
/* ****************** */

#MainWindow {
    background: {{ color.background.base }};
}


/* ****************** */
/*   2. Panel Chung   */
/* ****************** */

#Panel {
    background: {{ color.background.panel }};
    padding: 12px;
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
}


/* ****************** */
/*   3. Side Panel    */
/* ****************** */

/* 3.1 Navigation Buttons */
QPushButton[nav="true"] {
    text-align: left;
    padding: 12px 16px;
    background: transparent;

    border-radius: 12px;
    border: 1px solid transparent;

    font-size: {{ typography.secondary.size }}px;
    font-weight: {{ typography.secondary.weight }};
    color: {{ color.text.primary }};
}

QPushButton[nav="true"]:hover {
    background: {{ color.state.secondary.hover }};
    border: 1px solid #e3e5e6ff;
}

QPushButton[nav="true"]:checked {
    background: {{ color.state.secondary.active }};
    color: {{ color.text.secondary }};
}

/* 3.2 User Info */
#UserLabel {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
}

#VersionLabel {
    font-size: {{ typography.muted.size }}px;
    color: {{ color.text.muted }};
}

/* ****************** */
/*   4. Base Page     */
/* ****************** */

#PageHeader {
    font-size: {{ typography.heading1.size }}px;
    font-weight: {{ typography.heading1.weight }};
    color: {{ color.text.primary }};
}

