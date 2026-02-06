import os
from typing import Optional, List
from git import Repo, InvalidGitRepositoryError, GitCommandError

class GitHandler:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            self.repo = None

    def init_repo(self) -> Repo:
        """Initialize a new git repository if it doesn't exist."""
        if not self.repo:
            self.repo = Repo.init(self.repo_path)
        return self.repo

    def add_and_commit(self, file_paths: List[str], message: str):
        """Add files and commit changes."""
        if not self.repo:
            self.init_repo()
        
        try:
            self.repo.index.add(file_paths)
            self.repo.index.commit(message)
        except GitCommandError as e:
            print(f"Error committing changes: {e}")
            raise

    def get_diff(self, file_path: str, rev1: str = "HEAD~1", rev2: str = "HEAD") -> str:
        """Get diff between two revisions for a specific file."""
        if not self.repo:
            return ""
        try:
            return self.repo.git.diff(rev1, rev2, file_path)
        except GitCommandError:
            return "No changes found or invalid revision."

    def get_history(self, file_path: str) -> List[dict]:
        """Get commit history for a specific file."""
        if not self.repo:
            return []
        
        history = []
        try:
            commits = list(self.repo.iter_commits(paths=file_path))
            for commit in commits:
                history.append({
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "date": commit.authored_datetime.isoformat(),
                    "message": commit.message.strip()
                })
        except GitCommandError:
            pass
        return history

    def get_blame(self, file_path: str) -> List[tuple]:
        """Get blame information for a file."""
        if not self.repo:
            return []
        try:
            return self.repo.blame("HEAD", file_path)
        except GitCommandError:
            return []
