"""Output formatting."""

import json
from dataclasses import asdict
from typing import Any


class OutputFormatter:
    """Format output for different formats."""

    def __init__(self, format_type: str = "plain") -> None:
        self.format_type = format_type

    def format(self, data: Any) -> str:
        """Format data according to the output type."""
        if self.format_type == "json":
            if isinstance(data, dict) or isinstance(data, list):
                return json.dumps(data, ensure_ascii=False, indent=2)
            return json.dumps(asdict(data), ensure_ascii=False, indent=2)
        return str(data)

    def print(self, data: Any) -> None:
        """Print formatted data."""
        print(self.format(data))
