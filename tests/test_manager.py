import pytest
import os
import shutil
from prompt_mgr.manager import PromptManager


@pytest.fixture
def temp_project(tmp_path):
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    # Create a dummy README
    (project_dir / "README.md").write_text("# Test Project")
    return str(project_dir)


def test_init_project(temp_project):
    mgr = PromptManager(temp_project)
    mgr.init_project()
    assert os.path.exists(os.path.join(temp_project, "prompts"))
    assert os.path.exists(os.path.join(temp_project, "prompts", "welcome.yaml"))
    assert os.path.exists(os.path.join(temp_project, ".git"))


def test_add_and_list_prompts(temp_project):
    mgr = PromptManager(temp_project)
    mgr.init_project()

    data = {
        "name": "Test Prompt",
        "description": "Desc",
        "template": "Hello {{ project_name }}",
        "tags": ["test"],
        "version": "0.1.0",
    }
    mgr.add_prompt("test_p.yaml", data)

    prompts = mgr.list_prompts()
    assert any(p["name"] == "Test Prompt" for p in prompts)
    assert any(p["filename"] == "test_p.yaml" for p in prompts)


def test_search_prompts(temp_project):
    mgr = PromptManager(temp_project)
    mgr.init_project()

    data = {
        "name": "Searchable Prompt",
        "description": "Find me",
        "template": "Template content",
        "tags": ["tag1"],
        "version": "0.1.0",
    }
    mgr.add_prompt("search.yaml", data)

    results = mgr.search_prompts("Find me")
    assert len(results) > 0
    assert results[0]["name"] == "Searchable Prompt"


def test_export_prompt(temp_project):
    mgr = PromptManager(temp_project)
    mgr.init_project()

    data = {
        "name": "Context Prompt",
        "description": "Test context",
        "template": "Project: {{ project_name }}",
        "tags": [],
        "version": "0.1.0",
    }
    mgr.add_prompt("context.yaml", data)

    exported = mgr.export_prompt("context.yaml", "yaml")
    assert "Project: test_project" in exported
