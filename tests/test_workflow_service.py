from promptlib.storage.sqlite import SQLiteRepository
from promptlib.services.rendering import RenderingService
from promptlib.services.prompt_service import PromptService
from promptlib.services.workflow_service import UltimateWorkflowService
from promptlib.models.workflow import Workflow, WorkflowStep
import os

def test_workflow_service():
    db_file = "test_workflow.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    repo = SQLiteRepository(f"sqlite:///{db_file}")
    svc = PromptService(repo, RenderingService())
    from promptlib.agents.engine import AgentOrchestrator
    wf_svc = UltimateWorkflowService(svc, AgentOrchestrator())

    p1 = svc.create_prompt("Step1", "Input is {{val}}")
    p2 = svc.create_prompt("Step2", "Step1 result was: {{prev_res}}")

    wf = Workflow(
        name="Test Workflow",
        start_step_id="s1",
        steps={
            "s1": WorkflowStep(id="s1", prompt_id=p1.id, input_mapping={"val": "input_val"}, output_key="res1", next_step_id="s2"),
            "s2": WorkflowStep(id="s2", prompt_id=p2.id, input_mapping={"prev_res": "res1"}, output_key="final")
        }
    )

    wf_svc.register_workflow(wf)
    result_context = wf_svc.run_workflow(str(wf.id), {"input_val": "HELLO"})

    assert result_context["res1"] == "Input is HELLO"
    assert result_context["final"] == "Step1 result was: Input is HELLO"

    os.remove(db_file)
    print("Workflow service test passed!")

if __name__ == "__main__":
    test_workflow_service()
