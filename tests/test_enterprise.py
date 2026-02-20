from promptlib.storage.sqlite import SQLiteRepository
from promptlib.services.rendering import RenderingService
from promptlib.services.prompt_service import PromptService
from promptlib.embeddings.engine import EmbeddingEngine
from promptlib.vector_index.faiss_index import VectorIndex
import os
import shutil

def test_enterprise_features():
    db_file = "test_enterprise.db"
    idx_file = "test_enterprise.index"
    cache_dir = "test_cache"

    for f in [db_file, idx_file, idx_file + ".ids"]:
        if os.path.exists(f): os.remove(f)
    if os.path.exists(cache_dir): shutil.rmtree(cache_dir)

    repo = SQLiteRepository(f"sqlite:///{db_file}")
    engine = EmbeddingEngine(cache_dir=cache_dir)
    idx = VectorIndex(dimension=engine.get_dimension(), index_path=idx_file)
    svc = PromptService(repo, RenderingService(), embedding_engine=engine, vector_index=idx)

    # Create prompts
    svc.create_prompt("SQL Expert", "You are an expert in SQL and databases.")
    svc.create_prompt("Art Critic", "You are a world-class art critic.")

    # Semantic Search
    results = svc.search_prompts("database query", semantic=True, k=1)
    assert len(results) == 1
    assert results[0].name == "SQL Expert"

    # Hybrid Search (Keyword match should also work)
    results = svc.search_prompts("Art", semantic=True, k=1)
    assert results[0].name == "Art Critic"

    # persistence test
    idx.save()
    assert os.path.exists(idx_file)

    # Clean up
    for f in [db_file, idx_file, idx_file + ".ids"]:
        if os.path.exists(f): os.remove(f)
    shutil.rmtree(cache_dir)
    print("Enterprise features test passed!")

if __name__ == "__main__":
    test_enterprise_features()
