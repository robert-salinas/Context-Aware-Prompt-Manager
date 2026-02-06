import pytest
from typer.testing import CliRunner
from prompt_mgr.cli import app
import os
import shutil

runner = CliRunner()

@pytest.fixture
def clean_cwd(tmp_path):
    old_cwd = os.getcwd()
    new_cwd = tmp_path / "cli_test"
    new_cwd.mkdir()
    os.chdir(new_cwd)
    yield new_cwd
    os.chdir(old_cwd)

def test_cli_init(clean_cwd):
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Success!" in result.stdout
    assert os.path.exists("prompts")
    assert os.path.exists(".prompt_mgr.db")

def test_cli_add_and_list(clean_cwd):
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["add", "Test Prompt", "Hello {{ project_name }}", "--tag", "test"])
    assert result.exit_code == 0
    assert "Prompt added" in result.stdout
    
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Test Prompt" in result.stdout

def test_cli_search(clean_cwd):
    runner.invoke(app, ["init"])
    runner.invoke(app, ["add", "Unique Name", "Content", "--desc", "Searching for this"])
    
    result = runner.invoke(app, ["search", "Searching"])
    assert result.exit_code == 0
    assert "Unique Name" in result.stdout

def test_cli_context(clean_cwd):
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["context"])
    assert result.exit_code == 0
    assert "project_name" in result.stdout
