from typing import Dict, Any, Optional
from uuid import UUID
from promptlib.models.workflow import Workflow
from promptlib.workflows.engine import AdvancedWorkflowEngine
from promptlib.services.prompt_service import PromptService
from promptlib.agents.engine import AgentOrchestrator

class UltimateWorkflowService:
    def __init__(self, prompt_service: PromptService, agent_orchestrator: AgentOrchestrator):
        self.engine = AdvancedWorkflowEngine(prompt_service, agent_orchestrator)
        self.repository = prompt_service.repository

    def register_workflow(self, workflow: Workflow):
        self.repository.save_workflow(workflow)

    def run_workflow(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Try as UUID first
        wf = None
        try:
            wf_uuid = UUID(workflow_id)
            wf = self.repository.get_workflow(wf_uuid)
        except ValueError:
            pass

        if not wf:
            import os
            # Try loading from file if it's a path
            if os.path.exists(workflow_id):
                import json
                with open(workflow_id, 'r') as f:
                    wf = Workflow(**json.load(f))
            else:
                # Search by name or other logic? For now just fail
                raise ValueError(f"Workflow {workflow_id} not found in repository or as file")

        return self.engine.execute(wf, context)
