# Arquitectura del Prompt Manager

## Visión General
El Context-Aware Prompt Manager es una herramienta de CLI diseñada para gestionar prompts de LLM de forma estructurada, versionada y consciente del contexto del proyecto.

## Componentes Principales

1.  **CLI (Typer):** Interfaz de usuario para interactuar con el sistema.
2.  **Manager:** Coordina las operaciones entre los diferentes módulos.
3.  **Git Handler:** Gestiona el versionado de los prompts utilizando GitPython. Cada cambio se guarda como un commit.
4.  **Context Analyzer:** Analiza el entorno del proyecto (archivos, estructura, stacks tecnológicos) para proveer variables dinámicas.
5.  **Search Index (SQLite FTS5):** Indexa el contenido y metadatos de los prompts para búsquedas rápidas.
6.  **Jinja2 Templating:** Permite el uso de variables como `{{ project_name }}` o `{{ tech_stack }}` dentro de los prompts.

## Flujo de Datos
1.  El usuario crea un prompt mediante `prompt-mgr add`.
2.  El Manager valida la estructura (Pydantic).
3.  Se guarda el archivo YAML en `prompts/`.
4.  Git Handler realiza un commit del nuevo archivo.
5.  Search Index actualiza la base de datos SQLite.
6.  Al exportar (`prompt-mgr export`), el Context Analyzer extrae datos del proyecto y Jinja2 los inyecta en el template.
