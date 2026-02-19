from promptlib.agents.engine import ExecutorAgent, AgentOrchestrator
from promptlib.models.agent import Agent
from unittest.mock import MagicMock
from uuid import uuid4

def test_agent_orchestration():
    mock_svc = MagicMock()
    mock_svc.render_prompt.return_value = "Rendered result"

    agent_model = Agent(name="TestExecutor", role="executor")
    executor = ExecutorAgent(agent_model, mock_svc)

    orchestrator = AgentOrchestrator()
    orchestrator.register_agent(agent_model.id, executor)

    result = orchestrator.run_agent(agent_model.id, {"prompt_id": uuid4(), "variables": {}})
    assert result["output"] == "Rendered result"
    print("Agent orchestration test passed!")

if __name__ == "__main__":
    test_agent_orchestration()
