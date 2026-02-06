import os
import yaml
from typing import List, Dict, Any, Optional
from jinja2 import Template
from .git_handler import GitHandler
from .search import SearchIndex
from .context_analyzer import ContextAnalyzer
from .validator import validate_prompt, PromptModel
from .formatter import Formatter

class PromptManager:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.prompts_dir = os.path.join(project_path, "prompts")
        self.db_path = os.path.join(project_path, ".prompt_mgr.db")
        
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)
            
        self.git = GitHandler(project_path)
        self.search_index = SearchIndex(self.db_path)
        self.analyzer = ContextAnalyzer(project_path)

    def init_project(self):
        """Initialize the project structure and git repo."""
        self.git.init_repo()
        # Create a sample prompt if it doesn't exist
        sample_path = os.path.join(self.prompts_dir, "welcome.yaml")
        if not os.path.exists(sample_path):
            sample_data = {
                "name": "Welcome Prompt",
                "description": "A simple welcome prompt to get you started",
                "template": "Hello! I am working on a {{ tech_stack | join(', ') }} project called {{ project_name }}.",
                "tags": ["initial", "sample"],
                "version": "0.1.0"
            }
            self.add_prompt("welcome.yaml", sample_data)

    def add_prompt(self, filename: str, data: Dict[str, Any]):
        """Add or update a prompt."""
        if not filename.endswith(".yaml"):
            filename += ".yaml"
            
        path = os.path.join(self.prompts_dir, filename)
        
        # Validate data
        validated_data = validate_prompt(data)
        
        # Save to file
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(validated_data.model_dump(), f, allow_unicode=True, sort_keys=False)
            
        # Index for search
        self.search_index.index_prompt(
            path=filename,
            name=validated_data.name,
            content=validated_data.template,
            tags=validated_data.tags,
            description=validated_data.description
        )
        
        # Commit to git
        self.git.add_and_commit([os.path.join("prompts", filename)], f"Add/Update prompt: {validated_data.name}")
        
        return path

    def list_prompts(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all prompts, optionally filtered by tag."""
        prompts = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".yaml"):
                path = os.path.join(self.prompts_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if tag and tag not in data.get("tags", []):
                        continue
                    data["filename"] = filename
                    prompts.append(data)
        return prompts

    def get_prompt(self, filename: str) -> Dict[str, Any]:
        """Get a specific prompt by filename."""
        if not filename.endswith(".yaml"):
            filename += ".yaml"
        path = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt {filename} not found.")
            
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def export_prompt(self, filename: str, format_type: str = "yaml") -> str:
        """Export a prompt with context filled in."""
        prompt_data = self.get_prompt(filename)
        context = self.analyzer.analyze()
        
        # Render template with context
        template = Template(prompt_data["template"])
        rendered_content = template.render(**context)
        
        # Create export version
        export_data = prompt_data.copy()
        export_data["template"] = rendered_content
        
        return Formatter.format_output(export_data, format_type)

    def search_prompts(self, query: str) -> List[Dict[str, Any]]:
        """Search prompts using FTS index."""
        return self.search_index.search(query)

    def get_diff(self, filename: str, rev1: str = "HEAD~1", rev2: str = "HEAD") -> str:
        """Get diff for a prompt."""
        if not filename.endswith(".yaml"):
            filename += ".yaml"
        rel_path = os.path.join("prompts", filename)
        return self.git.get_diff(rel_path, rev1, rev2)
