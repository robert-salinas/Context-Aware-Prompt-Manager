import pytest
import os
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


def test_rejects_prompt_path_traversal(temp_project):
    mgr = PromptManager(temp_project, auto_version=False)
    with pytest.raises(ValueError, match="rutas"):
        mgr.add_prompt(
            "../escape.yaml", {"name": "Escape", "description": "x", "template": "x"}
        )


def test_active_project_is_separate_from_library(tmp_path):
    library = tmp_path / "library"
    project = tmp_path / "customer-project"
    project.mkdir()
    (project / "package.json").write_text("{}", encoding="utf-8")
    mgr = PromptManager(str(project), str(library), auto_version=False)
    mgr.add_prompt(
        "context.yaml",
        {
            "name": "Context",
            "description": "x",
            "template": "{{ project_name }}: {{ tech_stack | join(', ') }}",
        },
    )
    assert mgr.render_prompt("context.yaml") == "customer-project: Node.js"
    assert (library / "prompts" / "context.yaml").exists()
    assert not (project / "prompts").exists()


def test_missing_context_variable_is_reported(temp_project):
    mgr = PromptManager(temp_project, auto_version=False)
    mgr.add_prompt(
        "invalid.yaml",
        {
            "name": "Invalid",
            "description": "x",
            "template": "{{ variable_that_does_not_exist }}",
        },
    )
    with pytest.raises(ValueError, match="Completa"):
        mgr.render_prompt("invalid.yaml")


def test_unicode_filename_and_required_variables(temp_project):
    mgr = PromptManager(temp_project, auto_version=False)
    mgr.add_prompt(
        "revisión_técnica.yaml",
        {
            "name": "Revisión",
            "description": "x",
            "template": "{{ codigo }} en {{ project_name }}",
        },
    )
    assert mgr.required_variables("revisión_técnica.yaml") == ["codigo"]
    assert mgr.render_prompt(
        "revisión_técnica.yaml", {"codigo": "print('ok')"}
    ).startswith("print")


def test_delete_prompt_removes_file_and_search_entry(temp_project):
    mgr = PromptManager(temp_project, auto_version=False)
    mgr.add_prompt(
        "delete_me.yaml",
        {"name": "Delete me", "description": "unique phrase", "template": "text"},
    )
    mgr.delete_prompt("delete_me.yaml")
    assert not (mgr.prompts_dir / "delete_me.yaml").exists()
    assert mgr.search_prompts("unique") == []
