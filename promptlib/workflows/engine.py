from typing import Dict, Any, List
from promptlib.models.workflow import Workflow, WorkflowStep, WorkflowCondition
from promptlib.core.exceptions import WorkflowError

class AdvancedWorkflowEngine:
    def __init__(self, prompt_service: Any, agent_orchestrator: Any):
        self.prompt_service = prompt_service
        self.agent_orchestrator = agent_orchestrator

    def _evaluate_condition(self, condition: WorkflowCondition, context: Dict[str, Any]) -> bool:
        val = context.get(condition.variable)
        if condition.operator == "eq":
            return val == condition.value
        if condition.operator == "neq":
            return val != condition.value
        if condition.operator == "contains":
            return condition.value in str(val)
        return False

    def execute(self, workflow: Workflow, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        context = initial_context.copy()
        current_step_id = workflow.start_step_id

        visited = set()

        while current_step_id:
            if current_step_id in visited:
                raise WorkflowError(f"Infinite loop detected at step {current_step_id}")
            visited.add(current_step_id)

            step = workflow.steps.get(current_step_id)
            if not step:
                raise WorkflowError(f"Step {current_step_id} not found in workflow")

            # Evaluate condition if present
            if step.condition:
                if self._evaluate_condition(step.condition, context):
                    current_step_id = step.on_true
                else:
                    current_step_id = step.on_false
                continue

            # Execute step (either Prompt or Agent)
            inputs = {target: context.get(source) for target, source in step.input_mapping.items()}

            result = None
            if step.agent_id:
                result_data = self.agent_orchestrator.run_agent(step.agent_id, inputs)
                result = result_data.get("output") or result_data.get("optimized")
            elif step.prompt_id:
                result = self.prompt_service.render_prompt(step.prompt_id, inputs)

            if step.output_key:
                context[step.output_key] = result

            current_step_id = step.next_step_id

        return context
