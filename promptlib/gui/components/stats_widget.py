
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar, QFrame, QScrollArea)
from PyQt6.QtCore import Qt

class StatsWidget(QWidget):
    def __init__(self, prompt_service):
        super().__init__()
        self.prompt_service = prompt_service
        self.init_ui()
        self.refresh_stats()

    def init_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel("لوحة المعلومات")
        header.setObjectName("header")
        layout.addWidget(header)

        # Summary Cards
        summary_layout = QHBoxLayout()

        self.total_prompts_card = self.create_card("إجمالي القوالب", "0")
        summary_layout.addWidget(self.total_prompts_card)

        self.total_usage_card = self.create_card("إجمالي الاستخدام", "0")
        summary_layout.addWidget(self.total_usage_card)

        layout.addLayout(summary_layout)

        # Categories Section
        layout.addWidget(QLabel("توزيع الفئات"))
        self.categories_container = QWidget()
        self.categories_layout = QVBoxLayout(self.categories_container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.categories_container)
        layout.addWidget(scroll)

    def create_card(self, title, value):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: #252525; border-radius: 10px; padding: 20px;")

        layout = QVBoxLayout(frame)
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        layout.addWidget(value_label)

        # Store label for updates
        frame.value_label = value_label
        return frame

    def refresh_stats(self):
        stats = self.prompt_service.get_stats()

        self.total_prompts_card.value_label.setText(str(stats["total_prompts"]))
        self.total_usage_card.value_label.setText(str(stats["total_usage"]))

        # Clear categories safely
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        categories = stats["categories"]
        total = stats["total_prompts"] or 1 # Avoid div by zero

        for cat, count in categories.items():
            cat_layout = QVBoxLayout()
            cat_info = QHBoxLayout()
            cat_info.addWidget(QLabel(cat))
            cat_info.addStretch()
            cat_info.addWidget(QLabel(str(count)))
            cat_layout.addLayout(cat_info)

            bar = QProgressBar()
            bar.setMaximum(total)
            bar.setValue(count)
            bar.setFormat(f"{(count/total)*100:.1f}%")
            cat_layout.addWidget(bar)

            container = QWidget()
            container.setLayout(cat_layout)
            self.categories_layout.addWidget(container)

        self.categories_layout.addStretch()
