
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLineEdit, QPushButton, QLabel, QScrollArea, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
import qtawesome as qta

class PromptDetailWidget(QWidget):
    prompt_updated = pyqtSignal()

    def __init__(self, prompt_service, rendering_service):
        super().__init__()
        self.prompt_service = prompt_service
        self.rendering_service = rendering_service
        self.current_prompt = None
        self.init_ui()

    def init_ui(self):
        # Set RTL for Arabic UI
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QVBoxLayout(self)

        # Header area
        header_layout = QHBoxLayout()
        self.title_label = QLabel("اختر قالباً")
        self.title_label.setObjectName("header")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.save_btn = QPushButton("حفظ التغييرات")
        self.save_btn.setIcon(qta.icon("fa5s.save"))
        self.save_btn.clicked.connect(self.save_prompt)
        self.save_btn.setEnabled(False)
        header_layout.addWidget(self.save_btn)

        layout.addLayout(header_layout)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Editor Widget
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.addWidget(QLabel("محتوى القالب:"))
        self.content_edit = QTextEdit()
        editor_layout.addWidget(self.content_edit)
        splitter.addWidget(editor_container)

        # Preview Widget
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)

        preview_header = QHBoxLayout()
        preview_header.addWidget(QLabel("معاينة النتيجة:"))
        preview_header.addStretch()

        self.render_btn = QPushButton("تشغيل")
        self.render_btn.setIcon(qta.icon("fa5s.play"))
        self.render_btn.clicked.connect(self.render_preview)
        preview_header.addWidget(self.render_btn)

        preview_layout.addLayout(preview_header)

        self.variables_input = QLineEdit()
        self.variables_input.setPlaceholderText('متغيرات JSON (مثال: {"name": "World"})')
        preview_layout.addWidget(self.variables_input)

        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setStyleSheet("background-color: #1a1a1a; color: #a0a0a0;")
        preview_layout.addWidget(self.preview_area)

        splitter.addWidget(preview_container)

        layout.addWidget(splitter)

    def set_prompt(self, prompt):
        self.current_prompt = prompt
        self.title_label.setText(f"{prompt.name} (v{prompt.version})")
        self.content_edit.setPlainText(prompt.content)
        self.preview_area.clear()
        self.save_btn.setEnabled(True)

    def save_prompt(self):
        if not self.current_prompt:
            return

        new_content = self.content_edit.toPlainText()
        try:
            updated = self.prompt_service.update_prompt(self.current_prompt.id, content=new_content)
            self.set_prompt(updated)
            self.prompt_updated.emit()
        except Exception as e:
            self.preview_area.setPlainText(f"خطأ أثناء الحفظ: {e}")

    def render_preview(self):
        if not self.current_prompt:
            return

        content = self.content_edit.toPlainText()
        variables_str = self.variables_input.text() or "{}"

        try:
            variables = json.loads(variables_str)
            # Use rendering service directly for unsaved content preview
            rendered = self.rendering_service.render(content, variables)
            self.preview_area.setPlainText(rendered)
        except Exception as e:
            self.preview_area.setPlainText(f"خطأ أثناء المعالجة: {e}")
