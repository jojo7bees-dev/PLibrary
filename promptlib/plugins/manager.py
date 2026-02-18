from abc import ABC
from typing import List, Any

class BasePlugin(ABC):
    def __init__(self, name: str):
        self.name = name

    def on_prompt_created(self, prompt: Any):
        pass

    def on_prompt_rendered(self, prompt: Any, rendered: str):
        pass

class PluginManager:
    def __init__(self):
        self.plugins: List[BasePlugin] = []

    def register_plugin(self, plugin: BasePlugin):
        self.plugins.append(plugin)

    def notify_prompt_created(self, prompt: Any):
        for plugin in self.plugins:
            try:
                plugin.on_prompt_created(prompt)
            except Exception as e:
                print(f"Plugin {plugin.name} error in on_prompt_created: {e}")

    def notify_prompt_rendered(self, prompt: Any, rendered: str):
        for plugin in self.plugins:
            try:
                plugin.on_prompt_rendered(prompt, rendered)
            except Exception as e:
                print(f"Plugin {plugin.name} error in on_prompt_rendered: {e}")
