from promptlib.workflows.engine import AdvancedWorkflowEngine
from promptlib.models.workflow import Workflow, WorkflowStep, WorkflowCondition
from unittest.mock import MagicMock
from uuid import uuid4

def test_advanced_workflow():
    mock_svc = MagicMock()
    mock_svc.render_prompt.side_effect = lambda pid, vars: f"Result for {vars.get('val')}"

    orchestrator = MagicMock()

    wf = Workflow(
        name="BranchingWF",
        start_step_id="step1",
        steps={
            "step1": WorkflowStep(id="step1", condition=WorkflowCondition(variable="input", operator="eq", value="A"), on_true="stepA", on_false="stepB"),
            "stepA": WorkflowStep(id="stepA", prompt_id=uuid4(), input_mapping={"val": "input"}, output_key="res"),
            "stepB": WorkflowStep(id="stepB", prompt_id=uuid4(), input_mapping={"val": "input"}, output_key="res")
        }
    )

    engine = AdvancedWorkflowEngine(mock_svc, orchestrator)

    # Test path A
    ctx_a = engine.execute(wf, {"input": "A"})
    assert ctx_a["res"] == "Result for A"

    # Test path B
    ctx_b = engine.execute(wf, {"input": "B"})
    assert ctx_b["res"] == "Result for B"

    print("Advanced workflow test passed!")

if __name__ == "__main__":
    test_advanced_workflow()
