import json

from prompt_mgr.formatter import Formatter
from prompt_mgr.settings import SettingsStore


def test_settings_save_and_reload(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    store = SettingsStore()
    store.settings.active_project = "C:/example"
    store.settings.ui_scale = 110
    store.save()
    loaded = SettingsStore()
    assert loaded.settings.active_project == "C:/example"
    assert loaded.settings.ui_scale == 110
    assert json.loads(loaded.path.read_text(encoding="utf-8"))["auto_version"] is False


def test_prepare_library_copies_defaults_once(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "data"))
    defaults = tmp_path / "defaults"
    defaults.mkdir()
    (defaults / "sample.yaml").write_text("name: Sample", encoding="utf-8")
    store = SettingsStore()
    library = store.prepare_library(defaults)
    assert (library / "prompts" / "sample.yaml").exists()
    (defaults / "sample.yaml").write_text("changed", encoding="utf-8")
    store.prepare_library(defaults)
    assert (library / "prompts" / "sample.yaml").read_text(
        encoding="utf-8"
    ) == "name: Sample"


def test_formatter_supports_all_public_formats():
    data = {
        "name": "Example",
        "description": "Desc",
        "tags": ["one"],
        "template": "Hello",
    }
    assert '"name": "Example"' in Formatter.format_output(data, "json")
    assert "name: Example" in Formatter.format_output(data, "yaml")
    assert "# Example" in Formatter.format_output(data, "markdown")


def test_library_migrates_legacy_placeholders_and_samples(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "data"))
    store = SettingsStore()
    prompts = store.library / "prompts"
    prompts.mkdir(parents=True)
    (prompts / "legacy.yaml").write_text("template: '[CÓDIGO]'", encoding="utf-8")
    (prompts / "testprompt.yaml").write_text("name: TestPrompt", encoding="utf-8")
    store.prepare_library(tmp_path / "missing")
    assert "{{ codigo }}" in (prompts / "legacy.yaml").read_text(encoding="utf-8")
    assert not (prompts / "testprompt.yaml").exists()
