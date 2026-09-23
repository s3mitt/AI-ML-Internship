"""Date Tool: Comprehensive date and time arithmetic, parsing, and formatting engine."""

from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from dateutil import parser as date_parser
from core.errors import ValidationError
from tools.base import BaseTool


class DateTool(BaseTool):
    """Calculates date differences, future/past offsets, weekday lookups, and format conversions."""

    name = "date_tool"
    description = (
        "Perform calendar calculations: get current date/time, determine day of week for any date, "
        "calculate days between two dates, add/subtract days to a date, and convert date formats."
    )
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Operation: 'current', 'day_of_week', 'days_between', 'add_days', or 'convert_format'.",
            },
            "date": {
                "type": "string",
                "description": "Primary date string (e.g. '2026-09-25', '25 September 2026').",
            },
            "start_date": {
                "type": "string",
                "description": "Start date for 'days_between' calculation.",
            },
            "end_date": {
                "type": "string",
                "description": "End date for 'days_between' calculation.",
            },
            "days": {
                "type": "integer",
                "description": "Number of days to add (positive) or subtract (negative) for 'add_days'.",
            },
            "target_format": {
                "type": "string",
                "description": "Target strftime format for 'convert_format' (e.g. '%d/%m/%Y', '%B %d, %Y').",
            },
        },
        "required": [],
    }
    examples = [
        {"action": "current"},
        {"action": "day_of_week", "date": "25 September 2026"},
        {"action": "days_between", "start_date": "2026-09-01", "end_date": "2026-09-25"},
        {"action": "add_days", "date": "2026-09-23", "days": 30},
        {"action": "convert_format", "date": "2026-09-25", "target_format": "%d-%m-%Y"},
    ]

    def _parse_date(self, date_str: str, field_name: str = "date") -> datetime:
        """Parse natural or ISO date strings with dateutil."""
        if not date_str or not str(date_str).strip():
            raise ValidationError(f"Date value for '{field_name}' cannot be empty.", tool_name=self.name)
        try:
            return date_parser.parse(str(date_str).strip())
        except (ValueError, OverflowError) as e:
            raise ValidationError(f"Invalid date format for '{field_name}': '{date_str}'. Details: {str(e)}", tool_name=self.name)

    def run(
        self,
        action: str = "current",
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: Optional[int] = None,
        target_format: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Execute date calculation."""
        action_clean = action.lower().strip() if action else "current"

        if action_clean == "current":
            now = datetime.now()
            return {
                "action": "current",
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "day_of_week": now.strftime("%A"),
                "iso": now.isoformat(),
            }

        elif action_clean == "day_of_week":
            if not date:
                raise ValidationError("Parameter 'date' is required for action 'day_of_week'.", tool_name=self.name)
            parsed = self._parse_date(date, "date")
            return {
                "action": "day_of_week",
                "input_date": date,
                "parsed_date": parsed.strftime("%Y-%m-%d"),
                "day_of_week": parsed.strftime("%A"),
            }

        elif action_clean == "days_between":
            if not start_date or not end_date:
                raise ValidationError(
                    "Both 'start_date' and 'end_date' are required for action 'days_between'.",
                    tool_name=self.name,
                )
            p_start = self._parse_date(start_date, "start_date")
            p_end = self._parse_date(end_date, "end_date")
            diff = (p_end.date() - p_start.date()).days
            return {
                "action": "days_between",
                "start_date": p_start.strftime("%Y-%m-%d"),
                "end_date": p_end.strftime("%Y-%m-%d"),
                "days_difference": diff,
                "absolute_days": abs(diff),
            }

        elif action_clean == "add_days":
            if not date:
                # If date is omitted, default to today
                base_dt = datetime.now()
                date_str = base_dt.strftime("%Y-%m-%d")
            else:
                base_dt = self._parse_date(date, "date")
                date_str = date

            if days is None:
                raise ValidationError("Parameter 'days' (integer) is required for action 'add_days'.", tool_name=self.name)

            new_dt = base_dt + timedelta(days=days)
            return {
                "action": "add_days",
                "base_date": base_dt.strftime("%Y-%m-%d"),
                "days_offset": days,
                "result_date": new_dt.strftime("%Y-%m-%d"),
                "day_of_week": new_dt.strftime("%A"),
                "formatted": new_dt.strftime("%d %B %Y"),
            }

        elif action_clean == "convert_format":
            if not date:
                raise ValidationError("Parameter 'date' is required for action 'convert_format'.", tool_name=self.name)
            target_fmt = target_format or "%d/%m/%Y"
            parsed = self._parse_date(date, "date")
            try:
                formatted_str = parsed.strftime(target_fmt)
            except ValueError as ve:
                raise ValidationError(f"Invalid strftime format '{target_fmt}': {ve}", tool_name=self.name)
            return {
                "action": "convert_format",
                "original_date": date,
                "target_format": target_fmt,
                "formatted_date": formatted_str,
            }

        else:
            raise ValidationError(
                f"Unknown action '{action}'. Supported actions: 'current', 'day_of_week', 'days_between', 'add_days', 'convert_format'.",
                tool_name=self.name,
            )
