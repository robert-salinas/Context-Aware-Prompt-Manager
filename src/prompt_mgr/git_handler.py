import os
from typing import Optional, List, Any, Dict, Union, Tuple
from git import Repo, InvalidGitRepositoryError, GitCommandError


class GitHandler:
    """
    Gestor de operaciones de Git para el versionado de prompts.
    Permite inicializar repositorios, realizar commits y obtener diferencias.
    """

    def __init__(self, repo_path: str) -> None:
        """
        Inicializa el GitHandler.

        Args:
            repo_path: Ruta al repositorio Git.
        """
        self.repo_path = repo_path
        self.repo: Optional[Repo] = None
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            self.repo = None

    def init_repo(self) -> Repo:
        """
        Inicializa un nuevo repositorio Git si no existe.

        Returns:
            Instancia del repositorio Git.
        """
        if not self.repo:
            self.repo = Repo.init(self.repo_path)
        return self.repo

    def add_and_commit(self, file_paths: List[str], message: str) -> None:
        """
        Añade archivos al índice y realiza un commit.

        Args:
            file_paths: Lista de rutas de archivos a añadir.
            message: Mensaje del commit.

        Raises:
            GitCommandError: Si ocurre un error durante la operación de Git.
        """
        if not self.repo:
            self.init_repo()

        assert self.repo is not None
        try:
            self.repo.index.add(file_paths)
            self.repo.index.commit(message)
        except GitCommandError as e:
            print(f"Error committing changes: {e}")
            raise

    def get_diff(self, file_path: str, rev1: str = "HEAD~1", rev2: str = "HEAD") -> str:
        """
        Obtiene la diferencia entre dos revisiones para un archivo específico.

        Args:
            file_path: Ruta del archivo.
            rev1: Revisión inicial.
            rev2: Revisión final.

        Returns:
            String con el diff o mensaje de error.
        """
        if not self.repo:
            return ""
        try:
            return str(self.repo.git.diff(rev1, rev2, file_path))
        except GitCommandError:
            return "No changes found or invalid revision."

    def get_history(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de commits para un archivo específico.

        Args:
            file_path: Ruta del archivo.

        Returns:
            Lista de diccionarios con la información de cada commit.
        """
        if not self.repo:
            return []

        history = []
        try:
            commits = list(self.repo.iter_commits(paths=file_path))
            for commit in commits:
                history.append(
                    {
                        "hash": commit.hexsha,
                        "author": str(commit.author.name),
                        "date": commit.authored_datetime.isoformat(),
                        "message": commit.message.strip(),
                    }
                )
        except (GitCommandError, AttributeError):
            pass
        return history

    def get_blame(self, file_path: str) -> List[Any]:
        """
        Obtiene información de 'blame' (autoría por línea) para un archivo.

        Args:
            file_path: Ruta del archivo.

        Returns:
            Lista con la información de blame.
        """
        if not self.repo:
            return []
        try:
            blame_data = self.repo.blame("HEAD", file_path)
            return list(blame_data) if blame_data else []
        except GitCommandError:
            return []
