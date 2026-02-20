
import sys
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from promptlib.gui.main_window import MainWindow
from promptlib.gui.components.list_widget import PromptListWidget
from promptlib.gui.components.detail_widget import PromptDetailWidget
from promptlib.gui.components.stats_widget import StatsWidget
from promptlib.gui.styles import apply_style

from promptlib.storage.sqlite import SQLiteRepository
from promptlib.config.settings import settings
from promptlib.services.prompt_service import PromptService
from promptlib.services.rendering import RenderingService

def main():
    # Initialize Core Services (similar to CLI)
    repo = SQLiteRepository(settings.sqlite_url)
    rendering_service = RenderingService()
    prompt_service = PromptService(repo, rendering_service)

    app = QApplication(sys.argv)
    # Set overall layout direction to RTL for Arabic
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    apply_style(app)

    window = MainWindow(prompt_service, rendering_service)

    # Setup Prompts View
    prompts_view = QWidget()
    prompts_layout = QHBoxLayout(prompts_view)

    list_widget = PromptListWidget(prompt_service)
    detail_widget = PromptDetailWidget(prompt_service, rendering_service)

    prompts_layout.addWidget(list_widget, 1)
    prompts_layout.addWidget(detail_widget, 2)

    # Connect signals
    list_widget.prompt_selected.connect(detail_widget.set_prompt)
    # Sync: Refresh list when detail view saves changes
    detail_widget.prompt_updated.connect(list_widget.refresh_list)

    window.set_prompts_widget(prompts_view)

    # Setup Stats View
    stats_widget = StatsWidget(prompt_service)
    window.set_stats_widget(stats_widget)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
