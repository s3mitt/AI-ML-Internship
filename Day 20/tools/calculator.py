"""Calculator Tool: Safe mathematical evaluator using AST parsing without unrestricted eval()."""

from __future__ import annotations
import ast
import operator
import re
from typing import Any, Dict, List, Union
from core.errors import SecurityError, ValidationError
from tools.base import BaseTool

# Safe operators whitelist
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class CalculatorTool(BaseTool):
    """Safely evaluates mathematical expressions, percentages, and averages without unsafe eval()."""

    name = "calculator"
    description = (
        "Safely evaluate arithmetic expressions (e.g. '25 * 48', '(25 + 15) * 2'), "
        "percentages (e.g. '15% of 800'), and averages (e.g. 'Average of 10, 20, 30')."
    )
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression, percentage query, or comma-separated numbers to average.",
            }
        },
        "required": ["expression"],
    }
    examples = [
        {"expression": "(25 + 15) * 2"},
        {"expression": "15% of 800"},
        {"expression": "Average of 10, 20, 30"},
    ]

    def _eval_ast(self, node: ast.AST) -> Union[int, float]:
        """Recursively evaluate an AST node strictly within the safe operator whitelist."""
        if isinstance(node, ast.Expression):
            return self._eval_ast(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValidationError(f"Unsupported constant type: {type(node.value).__name__}", tool_name=self.name)


        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in SAFE_OPERATORS:
                operand = self._eval_ast(node.operand)
                return SAFE_OPERATORS[op_type](operand)
            raise SecurityError(f"Unsupported unary operator: {op_type.__name__}", tool_name=self.name)

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in SAFE_OPERATORS:
                left = self._eval_ast(node.left)
                right = self._eval_ast(node.right)

                if op_type in (ast.Div, ast.FloorDiv, ast.Mod) and right == 0:
                    raise ValidationError("Division by zero is undefined.", tool_name=self.name)

                # Guard against huge power operations causing denial of service
                if op_type == ast.Pow and (right > 1000 or (isinstance(left, (int, float)) and abs(left) > 1000 and right > 100)):
                    raise ValidationError("Exponent is too large to evaluate safely.", tool_name=self.name)

                return SAFE_OPERATORS[op_type](left, right)
            raise SecurityError(f"Unsupported binary operator: {op_type.__name__}", tool_name=self.name)

        raise SecurityError(f"Unsafe or forbidden expression node: {type(node).__name__}", tool_name=self.name)

    def _parse_and_evaluate(self, expr_str: str) -> Union[int, float]:
        """Normalize high-level math formats like percentage and average, then evaluate via AST."""
        clean = expr_str.strip()

        # Handle 'Average of 10, 20, 30' or 'average(10, 20, 30)'
        avg_match = re.match(r"(?i)^average(?:\s*of|\s*\()?\s*([0-9\s,\.\-]+)\)?$", clean)
        if avg_match:
            raw_nums = avg_match.group(1).split(",")
            nums = []
            for n in raw_nums:
                n = n.strip()
                if not n:
                    continue
                try:
                    nums.append(float(n))
                except ValueError:
                    raise ValidationError(f"Invalid number in average list: '{n}'", tool_name=self.name)
            if not nums:
                raise ValidationError("No numbers provided for average calculation.", tool_name=self.name)
            result = sum(nums) / len(nums)
            return int(result) if result.is_integer() else round(result, 4)

        # Handle '15% of 800' or '15% * 800'
        pct_match = re.match(r"(?i)^(\d+(?:\.\d+)?)\s*%\s*(?:of|\*)\s*(\d+(?:\.\d+)?)$", clean)
        if pct_match:
            pct = float(pct_match.group(1))
            base = float(pct_match.group(2))
            res = (pct / 100.0) * base
            return int(res) if res.is_integer() else round(res, 4)

        # Normalize plain 'Calculate (25 + 15) * 2' or 'calculate 25 * 48'
        clean = re.sub(r"(?i)^calculate\s+", "", clean).strip()

        # Handle standalone percent inside expression, e.g. 15% -> (15/100)
        clean = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1 / 100)", clean)

        # Parse AST
        try:
            tree = ast.parse(clean, mode="eval")
        except SyntaxError as e:
            raise ValidationError(f"Malformed mathematical expression: '{clean}'. Details: {e.msg}", tool_name=self.name)

        result = self._eval_ast(tree)
        if isinstance(result, float) and result.is_integer():
            return int(result)
        if isinstance(result, float):
            return round(result, 6)
        return result

    def run(self, expression: str, **kwargs) -> Dict[str, Any]:
        """Execute calculation and return structured output."""
        if not expression or not expression.strip():
            raise ValidationError("Expression cannot be empty.", tool_name=self.name)

        res = self._parse_and_evaluate(expression)
        return {
            "expression": expression.strip(),
            "result": res,
            "status": "success",
        }
