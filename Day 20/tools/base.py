"""Base Tool class definition adhering to standard Function Calling specifications."""

from __future__ import annotations
import abc
import logging
from typing import Any, Dict, List, Optional
from core.errors import ToolError, ValidationError, make_error_response, make_success_response

logger = logging.getLogger("ToolEngine")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class BaseTool(abc.ABC):
    """Abstract Base Class for all executable tools in the agent system."""

    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema format
    examples: List[Dict[str, Any]] = []

    def __init__(self):
        if not hasattr(self, "name") or not self.name:
            raise ValueError(f"Tool {self.__class__.__name__} must define a unique 'name'.")
        if not hasattr(self, "description") or not self.description:
            raise ValueError(f"Tool {self.__class__.__name__} must define a 'description'.")
        if not hasattr(self, "parameters"):
            self.parameters = {"type": "object", "properties": {}, "required": []}

    def validate_inputs(self, kwargs: Dict[str, Any]) -> None:
        """Validate input parameters against schema constraints."""
        required = self.parameters.get("required", [])
        for req in required:
            if req not in kwargs or kwargs[req] is None or kwargs[req] == "":
                raise ValidationError(f"Missing required parameter '{req}'.", tool_name=self.name)

        properties = self.parameters.get("properties", {})
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": (list, tuple),
            "object": dict,
        }

        for param_name, val in kwargs.items():
            if param_name in properties and val is not None:
                expected_type_str = properties[param_name].get("type")
                if expected_type_str in type_map:
                    expected_python_type = type_map[expected_type_str]
                    # Note: bool is a subclass of int in Python, handle cleanly
                    if expected_type_str in ("integer", "number") and isinstance(val, bool):
                        raise ValidationError(
                            f"Parameter '{param_name}' expected {expected_type_str}, received bool.",
                            tool_name=self.name,
                        )
                    if not isinstance(val, expected_python_type):
                        raise ValidationError(
                            f"Parameter '{param_name}' expected {expected_type_str}, received {type(val).__name__}.",
                            tool_name=self.name,
                        )

    @abc.abstractmethod
    def run(self, **kwargs) -> Any:
        """Execution logic to be implemented by child classes."""
        raise NotImplementedError

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Public execution interface with input validation, logging, and error containment."""
        logger.info(f"Executing tool '{self.name}' with inputs: {kwargs}")
        try:
            self.validate_inputs(kwargs)
            result_data = self.run(**kwargs)
            logger.info(f"Tool '{self.name}' execution succeeded.")
            return make_success_response(data=result_data, tool=self.name)
        except ToolError as te:
            logger.warning(f"Tool '{self.name}' handled domain error: {te.message}")
            return te.to_dict()
        except Exception as exc:
            logger.error(f"Tool '{self.name}' unhandled exception: {exc}", exc_info=True)
            return make_error_response(
                error_type=type(exc).__name__,
                message=str(exc) or "An unexpected error occurred during execution.",
                tool=self.name,
            )

    def to_function_schema(self) -> Dict[str, Any]:
        """Export OpenAI/Gemini compatible function calling JSON schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
