import os
import json
from typing import Dict, Any, List
import yaml

class ContextAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = project_path

    def analyze(self) -> Dict[str, Any]:
        """Analyze the project and return context information."""
        context = {
            "project_name": os.path.basename(self.project_path),
            "tech_stack": self._detect_tech_stack(),
            "has_readme": self._has_file("README.md"),
            "has_tests": self._has_directory("tests") or self._has_directory("test"),
            "languages": self._detect_languages(),
            "structure": self._get_structure_summary()
        }
        
        # Try to extract more details from README if it exists
        if context["has_readme"]:
            context["readme_summary"] = self._summarize_readme()
            
        return context

    def _has_file(self, filename: str) -> bool:
        return os.path.isfile(os.path.join(self.project_path, filename))

    def _has_directory(self, dirname: str) -> bool:
        return os.path.isdir(os.path.join(self.project_path, dirname))

    def _detect_tech_stack(self) -> List[str]:
        stack = []
        if self._has_file("requirements.txt") or self._has_file("pyproject.toml"):
            stack.append("Python")
        if self._has_file("package.json"):
            stack.append("Node.js")
        if self._has_file("go.mod"):
            stack.append("Go")
        if self._has_file("pom.xml"):
            stack.append("Java/Maven")
        if self._has_file("Cargo.toml"):
            stack.append("Rust")
        return stack

    def _detect_languages(self) -> List[str]:
        langs = set()
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.endswith('.py'): langs.add("Python")
                elif f.endswith('.js') or f.endswith('.ts'): langs.add("JavaScript/TypeScript")
                elif f.endswith('.go'): langs.add("Go")
                elif f.endswith('.rs'): langs.add("Rust")
                elif f.endswith('.java'): langs.add("Java")
        return list(langs)

    def _get_structure_summary(self) -> str:
        """Returns a brief summary of the project structure."""
        items = os.listdir(self.project_path)
        dirs = [i for i in items if os.path.isdir(os.path.join(self.project_path, i)) and not i.startswith('.')]
        files = [i for i in items if os.path.isfile(os.path.join(self.project_path, i)) and not i.startswith('.')]
        return f"Dirs: {', '.join(dirs[:5])}; Files: {', '.join(files[:5])}"

    def _summarize_readme(self) -> str:
        """Extracts the first few lines of README."""
        readme_path = os.path.join(self.project_path, "README.md")
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read(500) # Read first 500 chars
                return content.strip()
        except Exception:
            return ""
