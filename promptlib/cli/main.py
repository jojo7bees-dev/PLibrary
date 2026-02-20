import typer
from typing import List, Optional
from uuid import UUID
import json
from promptlib.storage.sqlite import SQLiteRepository
from promptlib.storage.json_backend import JSONRepository
from promptlib.storage.yaml_backend import YAMLRepository
from promptlib.config.settings import settings
from promptlib.services.prompt_service import PromptService
from promptlib.services.rendering import RenderingService
from promptlib.embeddings.engine import EmbeddingEngine
from promptlib.vector_index.faiss_index import VectorIndex
from promptlib.services.workflow_service import UltimateWorkflowService
from promptlib.agents.engine import AgentOrchestrator, ExecutorAgent, OptimizerAgent
from promptlib.models.workflow import Workflow
from promptlib.models.agent import Agent
from promptlib.core.exceptions import PromptNotFoundError

app = typer.Typer(help="PromptLib - Advanced Local Prompt Management")

def get_repository():
    if settings.storage_backend == "sqlite":
        return SQLiteRepository(settings.sqlite_url)
    elif settings.storage_backend == "json":
        return JSONRepository(settings.json_dir)
    elif settings.storage_backend == "yaml":
        return YAMLRepository(settings.yaml_dir)
    else:
        raise ValueError(f"Unknown storage backend: {settings.storage_backend}")

# Global services (Lazy initialized in commands that need them)
_repo = None
_embedding_engine = None
_vector_index = None
_svc = None
_orchestrator = None
_wf_svc = None

def get_svc():
    global _repo, _embedding_engine, _vector_index, _svc
    if _svc is None:
        _repo = get_repository()
        _embedding_engine = EmbeddingEngine()
        _vector_index = VectorIndex(dimension=_embedding_engine.get_dimension(), index_path="promptlib.index")
        _svc = PromptService(_repo, RenderingService(), embedding_engine=_embedding_engine, vector_index=_vector_index)
    return _svc

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AgentOrchestrator()
        svc = get_svc()
        # Auto-register agents if they exist in repo
        # For simplicity, we'll register a default executor
        exec_model = Agent(name="DefaultExecutor", role="executor")
        _orchestrator.register_agent(exec_model.id, ExecutorAgent(exec_model, svc))
    return _orchestrator

def get_wf_svc():
    global _wf_svc
    if _wf_svc is None:
        _wf_svc = UltimateWorkflowService(get_svc(), get_orchestrator())
    return _wf_svc

@app.command()
def create(name: str, content: str, description: Optional[str] = None, category: Optional[str] = None, tags: Optional[str] = None):
    """Create a new prompt."""
    tag_list = tags.split(",") if tags else []
    prompt = get_svc().create_prompt(name=name, content=content, description=description, category=category, tags=tag_list)
    typer.echo(f"Created prompt '{prompt.name}' (ID: {prompt.id})")

@app.command()
def list(category: Optional[str] = None, tags: Optional[str] = None):
    """List all prompts."""
    tag_list = tags.split(",") if tags else None
    prompts = get_svc().list_prompts(category=category, tags=tag_list)
    for p in prompts:
        typer.echo(f"{p.id} | {p.name} | v{p.version} | {p.category or 'No category'}")

@app.command()
def delete(prompt_id: str):
    """Delete a prompt."""
    get_svc().delete_prompt(UUID(prompt_id))
    typer.echo(f"Deleted prompt {prompt_id}")

@app.command()
def edit(prompt_id: str, content: Optional[str] = None, description: Optional[str] = None, category: Optional[str] = None):
    """Update a prompt."""
    kwargs = {}
    if description is not None: kwargs["description"] = description
    if category is not None: kwargs["category"] = category

    prompt = get_svc().update_prompt(UUID(prompt_id), content=content, **kwargs)
    typer.echo(f"Updated prompt '{prompt.name}' to version {prompt.version}")

@app.command()
def search(query: str, semantic: bool = False, k: int = 5):
    """Search for prompts (keyword or semantic)."""
    results = get_svc().search_prompts(query, semantic=semantic, k=k)
    if not results:
        typer.echo("No results found.")
    for p in results:
        typer.echo(f"{p.id} | {p.name} | {p.content[:50]}...")

@app.command()
def reindex():
    """Rebuild the vector index."""
    svc = get_svc()
    svc.reindex()
    _vector_index.save()
    typer.echo("Vector index rebuilt and saved.")

@app.command()
def render(prompt_id: str, variables: str = typer.Option("{}", help="JSON string of variables")):
    """Render a prompt with variables (JSON string)."""
    try:
        vars_dict = json.loads(variables)
        rendered = get_svc().render_prompt(UUID(prompt_id), vars_dict)
        typer.echo(rendered)
    except Exception as e:
        typer.echo(f"Error: {e}")

@app.command()
def version(prompt_id: str, history: bool = False, rollback: Optional[str] = None, diff: Optional[str] = None):
    """Manage prompt versions."""
    svc = get_svc()
    if history:
        versions = svc.get_versions(UUID(prompt_id))
        for v in versions:
            typer.echo(f"{v.version} | {v.created_at} | {v.change_log}")
    elif rollback:
        prompt = svc.rollback(UUID(prompt_id), rollback)
        typer.echo(f"Rolled back to version {rollback}. New version is {prompt.version}")
    elif diff:
        # Expecting diff format "v1:v2"
        try:
            v1, v2 = diff.split(":")
            diff_text = svc.compare_versions(UUID(prompt_id), v1, v2)
            typer.echo(diff_text)
        except Exception as e:
            typer.echo(f"Error: {e}. Use format 'v1.0.0:1.0.1'")
    else:
        prompt = svc.get_prompt(UUID(prompt_id))
        typer.echo(f"Current version: {prompt.version}")

@app.command()
def lint(prompt_id: str):
    """Lint a prompt for optimization suggestions."""
    results = get_svc().lint_prompt(UUID(prompt_id))
    if not results:
        typer.echo("No issues found. Prompt looks great!")
    for res in results:
        typer.echo(str(res))

@app.command()
def optimize(prompt_id: str):
    """Automatically optimize a prompt."""
    result = get_svc().optimize_prompt(UUID(prompt_id))
    typer.echo(f"Original Content:\n{result.original_content}\n")
    typer.echo(f"Optimized Content:\n{result.optimized_content}\n")
    typer.echo("Suggestions:")
    for s in result.suggestions:
        typer.echo(f"  - {s.category}: {s.explanation}")
    typer.echo(f"Efficiency Score: {result.efficiency_score:.2f}")

@app.command()
def agent_run(agent_id: str, prompt_id: str, variables: str = "{}"):
    """Run an agent with a specific prompt."""
    try:
        vars_dict = json.loads(variables)
        res = get_orchestrator().run_agent(UUID(agent_id), {"prompt_id": prompt_id, "variables": vars_dict})
        typer.echo(json.dumps(res, indent=2))
    except Exception as e:
        typer.echo(f"Error: {e}")

@app.command()
def stats():
    """Get usage statistics."""
    s = get_svc().get_stats()
    typer.echo(f"Total Prompts: {s['total_prompts']}")
    typer.echo(f"Total Usage: {s['total_usage']}")
    typer.echo("Categories:")
    for cat, count in s['categories'].items():
        typer.echo(f"  - {cat}: {count}")

@app.command()
def workflow_run(workflow_id: str, context: str = "{}"):
    """Execute a workflow."""
    try:
        ctx_dict = json.loads(context)
        final_ctx = get_wf_svc().run_workflow(workflow_id, ctx_dict)
        typer.echo(json.dumps(final_ctx, indent=2))
    except Exception as e:
        typer.echo(f"Error: {e}")

if __name__ == "__main__":
    app()
