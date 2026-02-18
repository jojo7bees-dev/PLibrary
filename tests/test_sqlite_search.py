from promptlib.storage.sqlite import SQLiteRepository
from promptlib.models.prompt import Prompt
import os

def test_sqlite_search():
    db_file = "test_search.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    repo = SQLiteRepository(f"sqlite:///{db_file}")

    p1 = Prompt(name="Python Expert", content="You are an expert Python developer.", usage_count=10)
    p2 = Prompt(name="JavaScript Guru", content="You are an expert JavaScript developer.", usage_count=20)
    p3 = Prompt(name="Go Master", content="You are an expert Go developer.", usage_count=5)

    repo.save(p1)
    repo.save(p2)
    repo.save(p3)

    # Search by content
    results = repo.search("expert")
    assert len(results) == 3
    # Ranking by usage_count: p2 (20), p1 (10), p3 (5)
    assert results[0].name == "JavaScript Guru"
    assert results[1].name == "Python Expert"
    assert results[2].name == "Go Master"

    # Search by name
    results = repo.search("Python")
    assert len(results) == 1
    assert results[0].name == "Python Expert"

    os.remove(db_file)
    print("SQLite search and ranking test passed!")

if __name__ == "__main__":
    test_sqlite_search()
