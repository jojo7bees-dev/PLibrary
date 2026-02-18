from promptlib.plugins.manager import PluginManager, BasePlugin

class TestPlugin(BasePlugin):
    def on_prompt_created(self, prompt):
        print(f"Plugin notified of prompt: {prompt.name}")

def test_plugins():
    pm = PluginManager()
    p = TestPlugin("test")
    pm.register_plugin(p)

    from promptlib.models.prompt import Prompt
    pr = Prompt(name="hello", content="hi")
    pm.notify_prompt_created(pr)

if __name__ == "__main__":
    test_plugins()
