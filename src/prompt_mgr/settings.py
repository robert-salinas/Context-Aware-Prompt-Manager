"""Persistent desktop settings and writable prompt library."""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import shutil


@dataclass
class AppSettings:
    active_project: str = ""
    auto_version: bool = False
    theme: str = "Dark"
    ui_scale: int = 100


class SettingsStore:
    def __init__(self):
        self.root = Path(os.environ.get("APPDATA", Path.home())) / "RS-Prompt-Manager"
        self.path = self.root / "settings.json"
        self.library = self.root / "library"
        self.settings = AppSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            for key in asdict(self.settings):
                if key in data and type(data[key]) is type(getattr(self.settings, key)):
                    setattr(self.settings, key, data[key])
        except (OSError, ValueError):
            pass

    def prepare_library(self, bundled_prompts: Path) -> Path:
        prompts = self.library / "prompts"
        prompts.mkdir(parents=True, exist_ok=True)
        if not any(prompts.glob("*.yaml")) and bundled_prompts.exists():
            for source in bundled_prompts.glob("*.yaml"):
                shutil.copy2(source, prompts / source.name)
        self._migrate_legacy_prompts(prompts)
        return self.library

    def _migrate_legacy_prompts(self, prompts: Path) -> None:
        replacements = {
            "[FUNCION]": "{{ funcion }}",
            "[CÓDIGO]": "{{ codigo }}",
            "[QUERY]": "{{ consulta_sql }}",
            "[INSERTA CÓDIGO]": "{{ codigo }}",
            "{{ aws/azure/gcp }}": "{{ proveedor_cloud }}",
            "{{ aws/gcp/azure }}": "{{ proveedor_cloud }}",
            "{{ servicio/api }}": "{{ servicio_api }}",
            "{{ json/csv/sqlite }}": "{{ formato_salida }}",
            "{{ emocion/valor }}": "{{ emocion_valor }}",
        }
        for path in prompts.glob("*.yaml"):
            try:
                content = path.read_text(encoding="utf-8")
                if path.name == "testprompt.yaml" and "name: TestPrompt" in content:
                    path.unlink()
                    continue
                if path.name == "welcome.yaml" and "name: Welcome Prompt" in content:
                    path.unlink()
                    continue
                updated = content
                for legacy, jinja in replacements.items():
                    updated = updated.replace(legacy, jinja)
                if updated != content:
                    path.write_text(updated, encoding="utf-8")
            except OSError:
                continue

    def save(self):
        self.root.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(asdict(self.settings), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.path)
