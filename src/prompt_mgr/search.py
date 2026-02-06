import sqlite3
import os
from typing import List, Dict, Any

class SearchIndex:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with FTS5."""
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

    def index_prompt(self, path: str, name: str, content: str, tags: List[str], description: str):
        """Index or update a prompt in the search index."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete existing entry for this path
        cursor.execute("DELETE FROM prompts_fts WHERE path = ?", (path,))
        
        # Insert new entry
        tags_str = ",".join(tags)
        cursor.execute(
            "INSERT INTO prompts_fts (path, name, content, tags, description) VALUES (?, ?, ?, ?, ?)",
            (path, name, content, tags_str, description)
        )
        
        cursor.execute(
            "INSERT OR REPLACE INTO prompts_metadata (path, last_updated) VALUES (?, CURRENT_TIMESTAMP)",
            (path,)
        )
        
        conn.commit()
        conn.close()

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for prompts using FTS."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple search using MATCH
        # We can expand this with snippet() and rank
        cursor.execute("""
            SELECT path, name, description, tags, rank 
            FROM prompts_fts 
            WHERE prompts_fts MATCH ? 
            ORDER BY rank
        """, (query,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "path": row["path"],
                "name": row["name"],
                "description": row["description"],
                "tags": row["tags"].split(",") if row["tags"] else [],
                "rank": row["rank"]
            })
            
        conn.close()
        return results

    def remove_prompt(self, path: str):
        """Remove a prompt from the index."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM prompts_fts WHERE path = ?", (path,))
        cursor.execute("DELETE FROM prompts_metadata WHERE path = ?", (path,))
        conn.commit()
        conn.close()
