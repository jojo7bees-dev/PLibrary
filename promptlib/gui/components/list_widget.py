
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QLineEdit, QPushButton, QLabel, QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

class PromptListWidget(QWidget):
    prompt_selected = pyqtSignal(object)

    def __init__(self, prompt_service):
        super().__init__()
        self.prompt_service = prompt_service
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        # Set RTL for Arabic UI
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QVBoxLayout(self)

        # Header
        header = QLabel("قوالب المحادثة")
        header.setObjectName("header")
        layout.addWidget(header)

        # Search area
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("بحث عن القوالب...")
        self.search_input.textChanged.connect(self.search_prompts)
        search_layout.addWidget(self.search_input)

        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(qta.icon("fa5s.sync"))
        self.refresh_btn.clicked.connect(self.refresh_list)
        search_layout.addWidget(self.refresh_btn)

        layout.addLayout(search_layout)

        # List
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

    def refresh_list(self):
        self.list_widget.clear()
        prompts = self.prompt_service.list_prompts()
        for p in prompts:
            item = QListWidgetItem(f"{p.name} (v{p.version})")
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.list_widget.addItem(item)

    def search_prompts(self, text):
        if not text:
            self.refresh_list()
            return

        self.list_widget.clear()
        results = self.prompt_service.search_prompts(text)
        for p in results:
            item = QListWidgetItem(f"{p.name} (v{p.version})")
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.list_widget.addItem(item)

    def on_item_clicked(self, item):
        prompt = item.data(Qt.ItemDataRole.UserRole)
        self.prompt_selected.emit(prompt)
