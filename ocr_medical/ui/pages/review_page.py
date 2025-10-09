from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                                QPushButton, QFrame, QSlider, QSpinBox)
from PySide6.QtCore import Qt
from ocr_medical.ui.pages.base_page import BasePage
from ocr_medical.ui.style.theme_manager import ThemeManager


class ReviewPage(BasePage):
    """
    Trang đánh giá ứng dụng
    Cho phép người dùng rating và gửi feedback
    """
    def __init__(self, theme_manager: ThemeManager, parent=None) -> None:
        super().__init__("Review", theme_manager, parent)
        
        layout = self.layout()

        rating_frame = QFrame()
        rating_frame.setObjectName("RatingFrame")
        rating_layout = QVBoxLayout(rating_frame)
        
        rating_label = QLabel("How would you rate this application?")
        rating_label.setObjectName("RatingLabel")
        rating_layout.addWidget(rating_label)
        
        stars_layout = QHBoxLayout()
        stars_layout.addStretch(1)
        
        self.rating_buttons = []
        for i in range(1, 6):
            btn = QPushButton("★")
            btn.setObjectName("StarButton")
            btn.setFixedSize(50, 50)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, r=i: self._set_rating(r))
            self.rating_buttons.append(btn)
            stars_layout.addWidget(btn)
        
        stars_layout.addStretch(1)
        rating_layout.addLayout(stars_layout)
        
        self.rating_text = QLabel("No rating yet")
        self.rating_text.setObjectName("RatingText")
        self.rating_text.setAlignment(Qt.AlignCenter)
        rating_layout.addWidget(self.rating_text)
        
        layout.addWidget(rating_frame)

        feedback_label = QLabel("Your Feedback:")
        feedback_label.setObjectName("FeedbackLabel")
        layout.addWidget(feedback_label)
        
        self.feedback_text = QTextEdit()
        self.feedback_text.setObjectName("FeedbackText")
        self.feedback_text.setPlaceholderText("Share your thoughts about the application...")
        layout.addWidget(self.feedback_text)

        performance_label = QLabel("Performance Rating:")
        performance_label.setObjectName("PerformanceLabel")
        layout.addWidget(performance_label)
        
        perf_layout = QHBoxLayout()
        
        speed_layout = QVBoxLayout()
        speed_label = QLabel("Speed:")
        speed_layout.addWidget(speed_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        speed_layout.addWidget(self.speed_slider)
        perf_layout.addLayout(speed_layout)
        
        accuracy_layout = QVBoxLayout()
        accuracy_label = QLabel("Accuracy:")
        accuracy_layout.addWidget(accuracy_label)
        self.accuracy_slider = QSlider(Qt.Horizontal)
        self.accuracy_slider.setRange(1, 10)
        self.accuracy_slider.setValue(5)
        accuracy_layout.addWidget(self.accuracy_slider)
        perf_layout.addLayout(accuracy_layout)
        
        layout.addLayout(perf_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        self.submit_btn = QPushButton("Submit Review")
        self.submit_btn.setObjectName("SubmitButton")
        self.submit_btn.clicked.connect(self._submit_review)
        btn_layout.addWidget(self.submit_btn)
        
        layout.addLayout(btn_layout)

        layout.addStretch(1)
        
        self.current_rating = 0

    def _set_rating(self, rating: int):
        self.current_rating = rating
        
        for i, btn in enumerate(self.rating_buttons):
            if i < rating:
                btn.setStyleSheet("color: #FFD700; font-size: 24px;")
            else:
                btn.setStyleSheet("color: #ddd; font-size: 24px;")
        
        rating_texts = ["", "Poor", "Fair", "Good", "Very Good", "Excellent"]
        self.rating_text.setText(f"{rating}/5 - {rating_texts[rating]}")

    def _submit_review(self):
        from PySide6.QtWidgets import QMessageBox
        
        if self.current_rating == 0:
            QMessageBox.warning(self, "No Rating", "Please select a star rating first.")
            return
        
        feedback = self.feedback_text.toPlainText()
        speed = self.speed_slider.value()
        accuracy = self.accuracy_slider.value()
        
        review_data = {
            "rating": self.current_rating,
            "feedback": feedback,
            "speed": speed,
            "accuracy": accuracy
        }
        
        QMessageBox.information(
            self, 
            "Thank You!", 
            f"Thank you for your {self.current_rating}-star review!\n\nYour feedback helps us improve."
        )
        
        self.feedback_text.clear()
        self._set_rating(0)
        self.speed_slider.setValue(5)
        self.accuracy_slider.setValue(5)