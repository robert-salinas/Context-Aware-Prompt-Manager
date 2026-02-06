# ADR 0003: Implementación de búsqueda Full-Text (FTS)

## Estatus
Aceptado

## Contexto
A medida que el número de prompts crece, la búsqueda simple por nombre de archivo es insuficiente. El usuario debe poder buscar por el contenido del template, etiquetas o descripción.

## Decisión
Utilizar SQLite con el módulo FTS5 (Full-Text Search) para indexar los prompts.
- Se crea una tabla virtual `prompts_fts` que almacena el contenido indexable.
- Cada vez que se añade o actualiza un prompt (`prompt-mgr add`), se actualiza el índice.
- Las búsquedas se realizan mediante el operador `MATCH` de SQLite.

## Consecuencias
- **Pros:** Búsquedas extremadamente rápidas (< 10ms para colecciones medianas), soporte para operadores de búsqueda avanzada.
- **Contras:** Requiere mantener sincronizado el sistema de archivos (YAML) con la base de datos SQLite.
