from promptlib.storage.sqlite import SQLiteRepository
from promptlib.models.prompt import Prompt
import os

def test_sqlite_crud():
    db_file = "test_promptlib.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    repo = SQLiteRepository(f"sqlite:///{db_file}")

    p = Prompt(name="test_prompt", content="Hello {{name}}")
    repo.save(p)

    p2 = repo.get_by_name("test_prompt")
    assert p2 is not None
    assert p2.name == "test_prompt"
    assert p2.content == "Hello {{name}}"

    p2.description = "Updated description"
    repo.save(p2)

    p3 = repo.get_by_id(p.id)
    assert p3.description == "Updated description"

    repo.delete(p.id)
    assert repo.get_by_id(p.id) is None

    os.remove(db_file)
    print("SQLite CRUD test passed!")

if __name__ == "__main__":
    test_sqlite_crud()
