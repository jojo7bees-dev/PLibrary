from promptlib.services.rendering import RenderingService
import pytest
from promptlib.core.exceptions import ValidationError

def test_rendering():
    service = RenderingService()
    template = "Hello {{name}}, welcome to {{place}}!"

    # Extract variables
    vars = service.extract_variables(template)
    assert set(vars) == {"name", "place"}

    # Render successfully
    result = service.render(template, {"name": "Alice", "place": "Wonderland"})
    assert result == "Hello Alice, welcome to Wonderland!"

    # Missing variables
    try:
        service.validate_variables(template, {"name": "Alice"})
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        assert "Missing required variable: place" in str(e)

    print("Rendering service test passed!")

if __name__ == "__main__":
    test_rendering()
