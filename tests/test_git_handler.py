import pytest
import os
from prompt_mgr.git_handler import GitHandler


@pytest.fixture
def git_repo(tmp_path):
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    return str(repo_path)


def test_git_init(git_repo):
    handler = GitHandler(git_repo)
    handler.init_repo()
    assert os.path.exists(os.path.join(git_repo, ".git"))


def test_git_add_commit(git_repo):
    handler = GitHandler(git_repo)
    handler.init_repo()

    test_file = os.path.join(git_repo, "test.txt")
    with open(test_file, "w") as f:
        f.write("hello")

    handler.add_and_commit(["test.txt"], "initial commit")

    history = handler.get_history("test.txt")
    assert len(history) == 1
    assert history[0]["message"] == "initial commit"


def test_git_diff(git_repo):
    handler = GitHandler(git_repo)
    handler.init_repo()

    test_file = os.path.join(git_repo, "test.txt")
    with open(test_file, "w") as f:
        f.write("version 1")
    handler.add_and_commit(["test.txt"], "v1")

    with open(test_file, "w") as f:
        f.write("version 2")
    handler.add_and_commit(["test.txt"], "v2")

    diff = handler.get_diff("test.txt", "HEAD~1", "HEAD")
    assert "+version 2" in diff
    assert "-version 1" in diff
