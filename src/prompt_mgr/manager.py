"""Prompt library, contextual rendering, search and optional Git history."""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional

import yaml
from jinja2 import Environment, StrictUndefined, TemplateError, meta

from .context_analyzer import ContextAnalyzer
from .formatter import Formatter
from .git_handler import GitHandler
from .search import SearchIndex
from .validator import validate_prompt

SAFE_FILENAME = re.compile(r"^[^\W\d][\w-]{0,79}\.ya?ml$", re.UNICODE)


class PromptManager:
    """Manage a YAML prompt library and render it for one active project."""

    def __init__(
        self,
        project_path: str,
        library_path: Optional[str] = None,
        db_path: Optional[str] = None,
        auto_version: bool = True,
    ) -> None:
        self.project_path = str(Path(project_path).resolve())
        self.library_path = Path(library_path or project_path).resolve()
        self.prompts_dir = self.library_path / "prompts"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = (
            str(Path(db_path).resolve())
            if db_path
            else str(self.library_path / ".prompt_mgr.db")
        )
        self.auto_version = auto_version
        self.git = GitHandler(str(self.library_path))
        self.search_index = SearchIndex(self.db_path)
        self.analyzer = ContextAnalyzer(self.project_path)
        self._context_cache: Optional[Dict[str, Any]] = None
        self.environment = Environment(undefined=StrictUndefined, autoescape=False)
        self.rebuild_index()

    def set_active_project(self, project_path: str) -> None:
        path = Path(project_path).expanduser().resolve()
        if not path.is_dir():
            raise ValueError("La carpeta del proyecto activo no existe.")
        self.project_path = str(path)
        self.analyzer = ContextAnalyzer(self.project_path)
        self._context_cache = None

    def init_project(self, seed_sample: bool = True) -> None:
        if self.auto_version:
            self.git.init_repo()
        if seed_sample and not (self.prompts_dir / "welcome.yaml").exists():
            self.add_prompt(
                "welcome.yaml",
                {
                    "name": "Welcome Prompt",
                    "description": "Prompt inicial con contexto del proyecto",
                    "template": "Trabajo en {{ project_name }} con {{ tech_stack | join(', ') }}.",
                    "tags": ["initial", "sample"],
                    "version": "0.1.0",
                },
            )

    def _safe_filename(self, filename: str) -> str:
        original = filename
        if not filename.endswith((".yaml", ".yml")):
            filename += ".yaml"
        if Path(filename).name != filename or any(
            token in original for token in ("/", "\\", "..")
        ):
            raise ValueError("El nombre del prompt no puede contener rutas.")
        if not SAFE_FILENAME.fullmatch(filename):
            raise ValueError(
                "Usa letras, números, guiones o guiones bajos en el archivo."
            )
        return filename

    def add_prompt(self, filename: str, data: Dict[str, Any]) -> str:
        filename = self._safe_filename(filename)
        validated = validate_prompt(data)
        path = self.prompts_dir / filename
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(
            yaml.safe_dump(validated.model_dump(), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        temporary.replace(path)
        self.search_index.index_prompt(
            filename,
            validated.name,
            validated.template,
            validated.tags,
            validated.description,
        )
        if self.auto_version:
            self.git.add_and_commit(
                [str(Path("prompts") / filename)], f"Prompt: {validated.name}"
            )
        return str(path)

    def list_prompts(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        prompts = []
        for path in sorted(self.prompts_dir.glob("*.y*ml")):
            try:
                data = validate_prompt(
                    yaml.safe_load(path.read_text(encoding="utf-8"))
                ).model_dump()
            except (OSError, ValueError, TypeError):
                continue
            if tag and tag not in data.get("tags", []):
                continue
            data["filename"] = path.name
            prompts.append(data)
        return prompts

    def get_prompt(self, filename: str) -> Dict[str, Any]:
        filename = self._safe_filename(filename)
        path = self.prompts_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt {filename} no encontrado.")
        return validate_prompt(
            yaml.safe_load(path.read_text(encoding="utf-8"))
        ).model_dump()

    def context(self, refresh: bool = False) -> Dict[str, Any]:
        if refresh or self._context_cache is None:
            self._context_cache = self.analyzer.analyze()
        return dict(self._context_cache)

    def required_variables(self, filename: str) -> List[str]:
        source = self.get_prompt(filename)["template"]
        referenced = meta.find_undeclared_variables(self.environment.parse(source))
        return sorted(referenced.difference(self.context()))

    def render_prompt(
        self, filename: str, variables: Optional[Dict[str, str]] = None
    ) -> str:
        try:
            values: Dict[str, Any] = self.context()
            values.update(variables or {})
            missing = [
                name
                for name in self.required_variables(filename)
                if not str(values.get(name, "")).strip()
            ]
            if missing:
                raise ValueError("Completa: " + ", ".join(missing))
            return str(
                self.environment.from_string(
                    self.get_prompt(filename)["template"]
                ).render(**values)
            )
        except TemplateError as exc:
            raise ValueError(f"No se pudo resolver el contexto: {exc}") from exc

    def export_prompt(
        self,
        filename: str,
        format_type: str = "yaml",
        variables: Optional[Dict[str, str]] = None,
    ) -> str:
        data = self.get_prompt(filename)
        data["template"] = self.render_prompt(filename, variables)
        return Formatter.format_output(data, format_type)

    def search_prompts(self, query: str) -> List[Dict[str, Any]]:
        return (
            self.search_index.search(query.strip())
            if query.strip()
            else self.list_prompts()
        )

    def rebuild_index(self) -> None:
        for prompt in self.list_prompts():
            self.search_index.index_prompt(
                prompt["filename"],
                prompt["name"],
                prompt["template"],
                prompt["tags"],
                prompt["description"],
            )

    def get_diff(self, filename: str, rev1: str = "HEAD~1", rev2: str = "HEAD") -> str:
        return self.git.get_diff(
            str(Path("prompts") / self._safe_filename(filename)), rev1, rev2
        )

    def get_history(self, filename: str) -> List[Dict[str, Any]]:
        return self.git.get_history(
            str(Path("prompts") / self._safe_filename(filename))
        )

    def delete_prompt(self, filename: str) -> None:
        filename = self._safe_filename(filename)
        path = self.prompts_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Prompt {filename} no encontrado.")
        path.unlink()
        self.search_index.remove_prompt(filename)
        if self.auto_version:
            self.git.commit_deletion(
                str(Path("prompts") / filename), f"Delete prompt: {filename}"
            )
