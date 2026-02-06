import json
import yaml
from typing import Any, Dict

class Formatter:
    @staticmethod
    def to_json(data: Any) -> str:
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def to_yaml(data: Any) -> str:
        return yaml.dump(data, allow_unicode=True, sort_keys=False)

    @staticmethod
    def to_markdown(data: Dict[str, Any]) -> str:
        """Converts a prompt to a nice markdown format."""
        md = f"# {data.get('name', 'Unnamed Prompt')}\n\n"
        md += f"**Description:** {data.get('description', 'No description')}\n\n"
        md += f"**Tags:** {', '.join(data.get('tags', []))}\n\n"
        md += "## Template\n\n"
        md += "```\n"
        md += data.get('template', '')
        md += "\n```\n"
        return md

    @staticmethod
    def format_output(data: Any, format_type: str = "yaml") -> str:
        if format_type.lower() == "json":
            return Formatter.to_json(data)
        elif format_type.lower() == "markdown" or format_type.lower() == "md":
            if isinstance(data, dict):
                return Formatter.to_markdown(data)
            return str(data)
        else:
            return Formatter.to_yaml(data)
