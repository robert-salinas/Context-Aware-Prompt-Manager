# Arquitectura

## Responsabilidades

- `PromptManager`: biblioteca YAML, renderizado Jinja2 estricto, índice y versiones.
- `ContextAnalyzer`: señales estructurales del proyecto activo; no interpreta semánticamente el código.
- `SearchIndex`: índice local SQLite FTS5 reconstruible desde YAML.
- `GitHandler`: historial opcional de la biblioteca, separado del repositorio analizado.
- `SettingsStore`: preferencias y biblioteca escribible bajo `%APPDATA%\RS-Prompt-Manager`.
- `gui.py`: selección explícita de proyecto, catálogo, vista previa, editor y exportación.

## Flujo

1. La GUI abre la biblioteca local y el proyecto activo guardado.
2. El usuario puede cambiar el proyecto sin escribir nada dentro de él.
3. La búsqueda consulta FTS5 y devuelve los YAML correspondientes.
4. La vista contextualizada usa Jinja2 con `StrictUndefined`; una variable ausente bloquea la copia contextualizada y se muestra como error.
5. Guardar un prompt escribe primero un temporal y después reemplaza el YAML.
6. Si el usuario activó el historial, Git registra el cambio en la biblioteca local.

Los YAML son la fuente de verdad. SQLite y Git aportan búsqueda e historial; ninguno reemplaza el almacenamiento principal.
