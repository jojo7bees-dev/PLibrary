from promptlib.storage.sqlite import SQLiteRepository
from promptlib.services.rendering import RenderingService
from promptlib.services.prompt_service import PromptService
import os

def test_prompt_service():
    db_file = "test_service.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    repo = SQLiteRepository(f"sqlite:///{db_file}")
    render_svc = RenderingService()
    svc = PromptService(repo, render_svc)

    # Create
    p = svc.create_prompt("Test", "Hello {{name}}", description="Initial")
    assert p.version == "1.0.0"
    assert len(svc.get_versions(p.id)) == 1

    # Update
    p = svc.update_prompt(p.id, content="Hi {{name}}!", change_log="Changed greeting")
    assert p.version == "1.0.1"
    assert len(svc.get_versions(p.id)) == 2

    # Render
    rendered = svc.render_prompt(p.id, {"name": "Bob"})
    assert rendered == "Hi Bob!"

    p = svc.get_prompt(p.id)
    assert p.usage_count == 1

    # Rollback
    p = svc.rollback(p.id, "1.0.0")
    assert p.content == "Hello {{name}}"
    assert p.version == "1.0.2" # Rollback is a new version

    os.remove(db_file)
    print("Prompt service test passed!")

if __name__ == "__main__":
    test_prompt_service()
