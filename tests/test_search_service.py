from promptlib.storage.sqlite import SQLiteRepository
from promptlib.services.search import SearchService
from promptlib.models.prompt import Prompt
import os

def test_search_service():
    db_file = "test_search_svc.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    repo = SQLiteRepository(f"sqlite:///{db_file}")
    svc = SearchService(repo)

    repo.save(Prompt(name="Python Script", content="import os"))
    repo.save(Prompt(name="Java Program", content="public class"))

    # Exact match (via repo)
    res = svc.search("Python")
    assert len(res) == 1
    assert res[0].name == "Python Script"

    # Fuzzy match
    res = svc.search("Pythn") # Typo
    assert len(res) == 1
    assert res[0].name == "Python Script"

    os.remove(db_file)
    print("Search service test passed!")

if __name__ == "__main__":
    test_search_service()
