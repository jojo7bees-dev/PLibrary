from promptlib.storage.yaml_backend import YAMLRepository
from promptlib.models.prompt import Prompt
import shutil
import os

def test_yaml_crud():
    storage_dir = "test_prompts_yaml"
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)

    repo = YAMLRepository(storage_dir)

    p = Prompt(name="yaml_prompt", content="Hello YAML")
    repo.save(p)

    p2 = repo.get_by_id(p.id)
    assert p2 is not None
    assert p2.name == "yaml_prompt"

    repo.delete(p.id)
    assert repo.get_by_id(p.id) is None

    shutil.rmtree(storage_dir)
    print("YAML CRUD test passed!")

if __name__ == "__main__":
    test_yaml_crud()
