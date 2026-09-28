# RS Context Prompt Manager

**Biblioteca local de prompts con contexto visible, búsqueda y versionado opcional.**

Selecciona un proyecto, revisa el contexto estructural detectado y genera una versión final del prompt antes de copiarla o exportarla. La aplicación funciona localmente y no envía código ni prompts a servicios externos.

![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)
![Version 0.2.0](https://img.shields.io/badge/version-0.2.0-orange)
[![MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Inicio rápido · Windows

Abre `run_app.bat`. Una distribución que incluya `dist\RS-Context-Prompt-Manager.exe` se instala en `%LOCALAPPDATA%\RS-Prompt-Manager` y funciona sin Python. En desarrollo, el lanzador prepara Python 3.11 y registra los detalles en `%APPDATA%\RS-Prompt-Manager\install.log`.

- Preparar sin abrir: `run_app.bat --setup-only`
- Reparar instalación: `run_app.bat --repair`
- Desinstalar conservando la biblioteca: `uninstall.bat`
- Eliminar también la biblioteca: `uninstall.bat -RemoveLibrary`

## Flujo principal

1. Elige la carpeta del **proyecto activo**.
2. Busca y selecciona un prompt de la biblioteca.
3. Completa los campos que la plantilla necesita, como código, requisitos o producto.
4. Revisa la pestaña **Contextualizado** antes de copiar, o cambia a **Plantilla** para ver el Jinja2 original.
5. Copia el resultado o expórtalo como Markdown, JSON o YAML.

La acción principal es **Copiar contextualizado**. Nunca se presupone que el texto está listo si falta una variable.

Desde el panel de detalle también puedes editar, eliminar con confirmación, consultar el historial y exportar. Preferencias se abre dentro de la ventana principal, siguiendo el mismo patrón de navegación del estándar RS.

La selección queda resaltada, la búsqueda acepta signos y palabras parciales sin romper el índice, y los valores escritos se conservan durante la sesión al cambiar de prompt. También puedes importar un YAML existente o duplicar una plantilla como punto de partida.

## Contexto detectado

La herramienta detecta de forma estructural:

- nombre de la carpeta del proyecto;
- stacks indicados por `pyproject.toml`, `requirements.txt`, `package.json`, `go.mod`, `pom.xml` y `Cargo.toml`;
- lenguajes según extensiones de archivos;
- presencia de tests y README;
- resumen limitado de la estructura y los primeros párrafos del README.

No interpreta semánticamente todo el código ni sustituye una revisión humana. “Context-aware” significa que inyecta estos datos locales y verificables en plantillas Jinja2.

## Biblioteca y versiones

La biblioteca se guarda en `%APPDATA%\RS-Prompt-Manager\library`. Cada prompt es YAML y el índice de búsqueda usa SQLite FTS5. El proyecto analizado y la biblioteca están separados: abrir un repositorio no añade archivos ni commits dentro de él.

El historial Git de la biblioteca es opcional y se controla en Preferencias. Cuando está activo, cada guardado crea una versión consultable desde **Historial**.

Variables disponibles:

```jinja2
{{ project_name }}
{{ tech_stack | join(', ') }}
{{ languages | join(', ') }}
{{ has_tests }}
{{ has_readme }}
{{ structure }}
{{ readme_summary }}
```

## CLI

```powershell
prompt-mgr init
prompt-mgr add "Revisión Python" "Revisa {{ project_name }}" --tag python
prompt-mgr list
prompt-mgr search "python"
prompt-mgr export revision_python.yaml --format markdown
prompt-mgr context
prompt-mgr diff revision_python.yaml
```

La CLI usa la carpeta actual como biblioteca y proyecto activo para conservar compatibilidad. La GUI mantiene ambos conceptos separados.

## Desarrollo

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m black --check src tests
.venv\Scripts\python.exe -m flake8 src tests --max-line-length=100
./build_exe.ps1
```

`build_exe.ps1` genera el ejecutable portable en `dist`. Si Inno Setup está instalado, `build_installer.ps1` crea el instalador de Windows en `release`, con acceso directo, desinstalador y actualización sobre la instalación existente. `sign_release.ps1` firma ambos artefactos cuando se proporciona el thumbprint de un certificado de firma de código válido.

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md)
- [Uso](docs/USAGE.md)
- [Ejemplos](docs/EXAMPLES.md)
- [Solución de problemas](docs/TROUBLESHOOTING.md)
- [Contribución](CONTRIBUTING.md)

## Licencia

[MIT](LICENSE) · Robert Salinas · RS Digital
