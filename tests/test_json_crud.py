from promptlib.storage.json_backend import JSONRepository
from promptlib.models.prompt import Prompt
import shutil
import os

def test_json_crud():
    storage_dir = "test_prompts_json"
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)

    repo = JSONRepository(storage_dir)

    p = Prompt(name="json_prompt", content="Hello JSON")
    repo.save(p)

    p2 = repo.get_by_id(p.id)
    assert p2 is not None
    assert p2.name == "json_prompt"

    p3 = repo.get_by_name("json_prompt")
    assert p3 is not None
    assert p3.id == p.id

    repo.delete(p.id)
    assert repo.get_by_id(p.id) is None

    shutil.rmtree(storage_dir)
    print("JSON CRUD test passed!")

if __name__ == "__main__":
    test_json_crud()
