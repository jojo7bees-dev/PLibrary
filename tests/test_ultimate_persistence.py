from promptlib.storage.sqlite import SQLiteRepository
from promptlib.services.rendering import RenderingService
from promptlib.services.prompt_service import PromptService
from promptlib.services.workflow_service import UltimateWorkflowService
from promptlib.agents.engine import AgentOrchestrator
from promptlib.models.workflow import Workflow, WorkflowStep
import os

def test_ultimate_persistence():
    db_file = "test_ultimate.db"
    if os.path.exists(db_file): os.remove(db_file)

    repo = SQLiteRepository(f"sqlite:///{db_file}")
    svc = PromptService(repo, RenderingService())
    orchestrator = AgentOrchestrator()
    wf_svc = UltimateWorkflowService(svc, orchestrator)

    p1 = svc.create_prompt("Step1", "Hi")

    wf = Workflow(
        name="PersistedWF",
        start_step_id="s1",
        steps={
            "s1": WorkflowStep(id="s1", prompt_id=p1.id, output_key="res")
        }
    )

    # Register (Save to DB)
    wf_svc.register_workflow(wf)

    # Verify we can fetch it
    wf_id = str(wf.id)
    repo_wf = repo.get_workflow(wf.id)
    assert repo_wf is not None
    assert repo_wf.name == "PersistedWF"

    # Run via ID
    res = wf_svc.run_workflow(wf_id, {})
    assert res["res"] == "Hi"

    os.remove(db_file)
    print("Ultimate persistence test passed!")

if __name__ == "__main__":
    test_ultimate_persistence()
