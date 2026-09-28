import sqlite3
import re
from typing import List, Dict, Any


class SearchIndex:
    """
    Gestor del índice de búsqueda Full-Text Search (FTS).
    Utiliza SQLite FTS5 para indexar y buscar contenido de prompts.
    """

    def __init__(self, db_path: str) -> None:
        """
        Inicializa el índice de búsqueda.

        Args:
            db_path: Ruta al archivo de base de datos SQLite.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Inicializa la base de datos SQLite con FTS5."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create virtual table for FTS5
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS prompts_fts USING fts5(
                path,
                name,
                content,
                tags,
                description
            )
        """)

        # Create a regular table for metadata if needed
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts_metadata (
                path TEXT PRIMARY KEY,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def index_prompt(
        self, path: str, name: str, content: str, tags: List[str], description: str
    ) -> None:
        """
        Indexa o actualiza un prompt en el índice de búsqueda.

        Args:
            path: Ruta del archivo del prompt.
            name: Nombre del prompt.
            content: Contenido/Template del prompt.
            tags: Lista de etiquetas.
            description: Descripción del prompt.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete existing entry for this path
        cursor.execute("DELETE FROM prompts_fts WHERE path = ?", (path,))

        # Insert new entry
        tags_str = ",".join(tags)
        cursor.execute(
            "INSERT INTO prompts_fts "
            "(path, name, content, tags, description) VALUES (?, ?, ?, ?, ?)",
            (path, name, content, tags_str, description),
        )

        cursor.execute(
            "INSERT OR REPLACE INTO prompts_metadata "
            "(path, last_updated) VALUES (?, CURRENT_TIMESTAMP)",
            (path,),
        )

        conn.commit()
        conn.close()

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca prompts utilizando FTS5.

        Args:
            query: Término o expresión de búsqueda.

        Returns:
            Lista de resultados ordenados por relevancia.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Simple search using MATCH
        terms = re.findall(r"[\wáéíóúüñ]+", query.lower(), flags=re.UNICODE)
        if not terms:
            conn.close()
            return []
        safe_query = " AND ".join(f'"{term}"' for term in terms)
        cursor.execute(
            """
            SELECT path, name, content, description, tags, rank
            FROM prompts_fts
            WHERE prompts_fts MATCH ?
            ORDER BY rank
        """,
            (safe_query,),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                {
                    "path": row["path"],
                    "name": row["name"],
                    "content": row["content"],
                    "description": row["description"],
                    "tags": row["tags"].split(",") if row["tags"] else [],
                    "rank": row["rank"],
                }
            )

        conn.close()
        return results

    def remove_prompt(self, path: str) -> None:
        """
        Elimina un prompt del índice.

        Args:
            path: Ruta del archivo a eliminar.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompts_fts WHERE path = ?", (path,))
        cursor.execute("DELETE FROM prompts_metadata WHERE path = ?", (path,))
        conn.commit()
        conn.close()
