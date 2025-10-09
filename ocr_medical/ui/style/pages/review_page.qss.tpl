/* Review Page CSS */

#RatingFrame {
    border: 1px solid {{ color.border.default }};
    border-radius: 12px;
    padding: 20px;
    background: {{ color.background.panel }};
    margin-bottom: 16px;
}

#RatingLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
    margin-bottom: 12px;
}

#StarButton {
    background: transparent;
    border: none;
    font-size: 32px;
    color: #ddd;
}

#StarButton:hover {
    color: #FFD700;
}

#RatingText {
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.muted }};
    margin-top: 8px;
}

#FeedbackLabel, #PerformanceLabel {
    font-size: {{ typography.heading2.size }}px;
    font-weight: {{ typography.heading2.weight }};
    color: {{ color.text.primary }};
    margin-top: 12px;
    margin-bottom: 8px;
}

#FeedbackText {
    border: 1px solid {{ color.border.default }};
    border-radius: 8px;
    padding: 12px;
    font-size: {{ typography.normal.size }}px;
    color: {{ color.text.primary }};
    background: {{ color.background.panel }};
    min-height: 120px;
}

#SubmitButton {
    background: {{ color.text.secondary }};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 24px;
    font-size: {{ typography.normal.size }}px;
    font-weight: 700;
}

#SubmitButton:hover {
    background: {{ color.state.primary.hover }};
}