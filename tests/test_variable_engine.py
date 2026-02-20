from promptlib.storage.sqlite import SQLiteRepository
from promptlib.services.rendering import RenderingService
from promptlib.services.prompt_service import PromptService
from promptlib.models.variable import VariableDefinition
import os

def test_variable_engine():
    db_file = "test_vars.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    repo = SQLiteRepository(f"sqlite:///{db_file}")
    render_svc = RenderingService()
    svc = PromptService(repo, render_svc)

    # Create prompt with variable definition (default value)
    v_def = VariableDefinition(name="language", default_value="Python")
    p = svc.create_prompt("Test Vars", "Code in {{language}}", variable_definitions=[v_def])

    # Render without providing variable -> should use default
    rendered = svc.render_prompt(p.id, {})
    assert rendered == "Code in Python"

    # Render with providing variable -> should override default
    rendered = svc.render_prompt(p.id, {"language": "Rust"})
    assert rendered == "Code in Rust"

    os.remove(db_file)
    print("Variable engine test passed!")

if __name__ == "__main__":
    test_variable_engine()
