
DARK_THEME = """
QMainWindow {
    background-color: #121212;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif;
    font-size: 14px;
}

QListWidget {
    background-color: #252525;
    border: none;
    outline: none;
    padding: 5px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 2px;
}

QListWidget::item:selected {
    background-color: #3d5afe;
    color: white;
}

QListWidget::item:hover {
    background-color: #333333;
}

QPushButton {
    background-color: #3d5afe;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #536dfe;
}

QPushButton:pressed {
    background-color: #304ffe;
}

QPushButton#secondary {
    background-color: #424242;
}

QPushButton#secondary:hover {
    background-color: #616161;
}

QLineEdit, QTextEdit {
    background-color: #2c2c2c;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px;
    color: #ffffff;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #3d5afe;
}

QLabel#header {
    font-size: 24px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 10px;
}

QLabel#subheader {
    font-size: 18px;
    font-weight: 500;
    color: #bbbbbb;
    margin-bottom: 5px;
}

QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #424242;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QProgressBar {
    border: 1px solid #3d3d3d;
    border-radius: 5px;
    text-align: center;
    background-color: #2c2c2c;
}

QProgressBar::chunk {
    background-color: #3d5afe;
    width: 20px;
}
"""

def apply_style(app):
    app.setStyleSheet(DARK_THEME)
