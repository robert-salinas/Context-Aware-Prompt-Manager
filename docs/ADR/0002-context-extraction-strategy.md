# ADR 0002: Estrategia de extracción de contexto

## Estatus
Aceptado

## Contexto
El valor principal de la herramienta es generar prompts que entiendan el entorno del proyecto. Necesitamos definir qué archivos y estructuras analizar para obtener la mejor información sin comprometer el rendimiento.

## Decisión
Implementar un analizador multinivel que:
1.  **Detección de Stack:** Busca archivos de manifiesto (`package.json`, `pyproject.toml`, `go.mod`, etc.).
2.  **Análisis de Estructura:** Lista directorios y archivos principales (excluyendo carpetas ocultas y `node_modules`).
3.  **Resumen de Documentación:** Lee las primeras líneas del `README.md` para entender el propósito del proyecto.
4.  **Extracción de Metadatos:** Obtiene el nombre del proyecto desde el directorio raíz.

## Consecuencias
- **Pros:** Información relevante disponible como variables de Jinja2 (`tech_stack`, `project_name`, etc.).
- **Contras:** El análisis de archivos muy grandes podría ser lento (limitado a los primeros 500 caracteres del README).
