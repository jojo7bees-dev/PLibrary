
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QStackedWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
import qtawesome as qta

class MainWindow(QMainWindow):
    def __init__(self, prompt_service, rendering_service):
        super().__init__()
        self.prompt_service = prompt_service
        self.rendering_service = rendering_service

        self.setWindowTitle("PromptLib - الإدارة المتقدمة")
        self.resize(1200, 800)

        # Set RTL for Arabic UI
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setObjectName("sidebar")

        self.sidebar.addItem("القوالب")
        self.sidebar.addItem("الإحصائيات")

        # Set icons for sidebar items
        self.sidebar.item(0).setIcon(qta.icon("fa5s.terminal", color="white"))
        self.sidebar.item(1).setIcon(qta.icon("fa5s.chart-bar", color="white"))

        layout.addWidget(self.sidebar)

        # Content Area
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)

        # We will add actual widgets here in the following steps
        self.prompts_placeholder = QLabel("عرض القوالب")
        self.prompts_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_stack.addWidget(self.prompts_placeholder)

        self.stats_placeholder = QLabel("عرض الإحصائيات")
        self.stats_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_stack.addWidget(self.stats_placeholder)

        # Sidebar selection change
        self.sidebar.currentRowChanged.connect(self.display_view)
        self.sidebar.setCurrentRow(0)

    def display_view(self, index):
        self.content_stack.setCurrentIndex(index)

    def set_prompts_widget(self, widget):
        # Replace placeholder
        current_widget = self.content_stack.widget(0)
        self.content_stack.removeWidget(current_widget)
        self.content_stack.insertWidget(0, widget)

    def set_stats_widget(self, widget):
        # Replace placeholder
        current_widget = self.content_stack.widget(1)
        self.content_stack.removeWidget(current_widget)
        self.content_stack.insertWidget(1, widget)
