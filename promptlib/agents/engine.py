from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from promptlib.models.agent import Agent
from promptlib.core.exceptions import PromptLibError

class BaseAgent:
    def __init__(self, model: Agent):
        self.model = model

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class ExecutorAgent(BaseAgent):
    def __init__(self, model: Agent, prompt_service: Any):
        super().__init__(model)
        self.prompt_service = prompt_service

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt_id = input_data.get("prompt_id")
        variables = input_data.get("variables", {})
        if not prompt_id:
            raise PromptLibError("ExecutorAgent requires prompt_id")

        result = self.prompt_service.render_prompt(UUID(str(prompt_id)), variables)
        self.model.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt_id": str(prompt_id),
            "status": "success"
        })
        return {"output": result}

class OptimizerAgent(BaseAgent):
    def __init__(self, model: Agent, optimization_service: Any):
        super().__init__(model)
        self.optimization_service = optimization_service

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt_id = input_data.get("prompt_id")
        if not prompt_id:
            raise PromptLibError("OptimizerAgent requires prompt_id")

        result = self.optimization_service.optimize(UUID(str(prompt_id)))
        self.model.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt_id": str(prompt_id),
            "action": "optimize"
        })
        return {"optimized": result}

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[UUID, BaseAgent] = {}

    def register_agent(self, agent_id: UUID, agent: BaseAgent):
        self.agents[agent_id] = agent

    def run_agent(self, agent_id: UUID, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if agent_id not in self.agents:
            raise PromptLibError(f"Agent {agent_id} not found")
        return self.agents[agent_id].run(input_data)
