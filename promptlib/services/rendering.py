from jinja2 import Environment, meta, StrictUndefined, TemplateSyntaxError
from typing import Dict, Any, List
from promptlib.core.exceptions import ValidationError

class RenderingService:
    def __init__(self):
        self.env = Environment(undefined=StrictUndefined)

    def extract_variables(self, template_content: str) -> List[str]:
        try:
            ast = self.env.parse(template_content)
            return list(meta.find_undeclared_variables(ast))
        except TemplateSyntaxError as e:
            raise ValidationError(f"Invalid template syntax: {e}")

    def render(self, template_content: str, variables: Dict[str, Any]) -> str:
        try:
            template = self.env.from_string(template_content)
            return template.render(**variables)
        except Exception as e:
            raise ValidationError(f"Rendering failed: {e}")

    def validate_variables(self, template_content: str, provided_variables: Dict[str, Any], variable_definitions: List[Any] = None) -> Dict[str, Any]:
        required = self.extract_variables(template_content)
        final_variables = provided_variables.copy()

        # Apply definitions (defaults, types, etc.)
        definitions_dict = {d.name: d for d in (variable_definitions or [])}

        for var_name in required:
            definition = definitions_dict.get(var_name)

            if var_name not in final_variables:
                if definition and definition.default_value is not None:
                    final_variables[var_name] = definition.default_value
                elif definition and not definition.required:
                    final_variables[var_name] = ""
                else:
                    raise ValidationError(f"Missing required variable: {var_name}")

            # Basic type validation/conversion if definition exists
            if definition and var_name in final_variables:
                val = final_variables[var_name]
                if definition.type == "number":
                    try:
                        final_variables[var_name] = float(val)
                    except ValueError:
                        raise ValidationError(f"Variable {var_name} must be a number")
                elif definition.type == "boolean":
                    if isinstance(val, str):
                        final_variables[var_name] = val.lower() in ("true", "1", "yes")

        return final_variables
