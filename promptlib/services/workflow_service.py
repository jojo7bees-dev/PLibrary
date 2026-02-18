from typing import Dict, Any, List
from promptlib.models.workflow import Workflow, WorkflowStep
from promptlib.services.prompt_service import PromptService
from promptlib.core.exceptions import WorkflowError

class WorkflowService:
    def __init__(self, prompt_service: PromptService):
        self.prompt_service = prompt_service

    def execute_workflow(self, workflow: Workflow, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        context = initial_context.copy()

        for step in workflow.steps:
            # Resolve inputs for this step
            step_inputs = {}
            for target_var, source_var in step.input_mapping.items():
                if source_var not in context:
                    raise WorkflowError(f"Missing required input '{source_var}' for step '{step.id}'")
                step_inputs[target_var] = context[source_var]

            # Execute the prompt
            try:
                result = self.prompt_service.render_prompt(step.prompt_id, step_inputs)

                # Store output in context
                if step.output_key:
                    context[step.output_key] = result
                else:
                    context[f"{step.id}_result"] = result

            except Exception as e:
                raise WorkflowError(f"Error executing step '{step.id}': {e}")

        return context
