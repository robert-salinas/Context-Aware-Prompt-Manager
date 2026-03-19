# 🚀 Context-Aware Prompt Manager (CAPM) v0.1.0

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python: 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![Tests: passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Build: passing](https://img.shields.io/badge/build-passing-brightgreen.svg)

Context-Aware Prompt Manager (CAPM) es una herramienta de ingeniería diseñada para gestionar, versionar y optimizar tus prompts de LLM mediante la extracción automática del contexto de tu proyecto, asegurando que cada interacción con la IA sea precisa y relevante.

## ✨ Características
- **🔒 Versionado Nativo (Git):** Cada prompt cuenta con un historial completo de cambios, permitiendo auditoría, diffs y reversiones mediante Git.
- **🧠 Extracción Automática de Contexto:** Analiza la estructura del proyecto, detecta stacks tecnológicos (Python, Node, Go, etc.) y resume archivos clave como el README para inyectarlos en tus prompts.
- **⚡ Búsqueda de Alto Rendimiento:** Motor de búsqueda Full-Text Search (FTS) basado en SQLite para encontrar prompts por contenido, etiquetas o descripción en milisegundos.
- **🛠️ Templates Dinámicos:** Utiliza Jinja2 para crear prompts flexibles con variables como `{{ project_name }}`, `{{ tech_stack }}` y más.
- **🌐 Exportación Políglota:** Genera prompts listos para usar en múltiples formatos: JSON, YAML y Markdown.

## � Instalación Rápida
Para poner en marcha el proyecto en tu entorno local:

```bash
# 1. Clonar el repositorio
git clone https://github.com/robertesteban/Context-Aware-Prompt-Manager.git
cd Context-Aware-Prompt-Manager

# 2. Instalar dependencias en modo editable
pip install -e .
```

## �️ Uso Básico
Para gestionar y optimizar tus prompts de forma eficiente:

### Inicialización y Gestión
```bash
# Inicializar el gestor en el proyecto actual
prompt-mgr init

# Añadir un nuevo prompt con contexto dinámico
prompt-mgr add "Refactor" "Ayúdame a refactorizar este código en {{ tech_stack | join(', ') }}" --tag "refactoring"

# Listar todos los prompts registrados
prompt-mgr list

# Buscar un prompt específico por contenido
prompt-mgr search "refactorizar"
```

### Exportación y Contexto
```bash
# Exportar un prompt con el contexto del proyecto inyectado
prompt-mgr export refactor.yaml --format markdown

# Ver el contexto detectado automáticamente por la herramienta
prompt-mgr context

# Ver cambios entre versiones de un prompt
prompt-mgr diff refactor.yaml
```

---

## 🖥️ Interfaz Gráfica (GUI)
Para una experiencia visual e interactiva de ingeniería de prompts, puedes lanzar la aplicación de escritorio:

### Ejecución
```bash
# En Windows (Launcher Automático)
./run_app.bat

# Alternativo (Manual)
set PYTHONPATH=src
python -m prompt_mgr.gui
```

### Características de la GUI
*   📂 **Catálogo:** Explora, busca y copia prompts con un clic mediante Toasts no bloqueantes.
*   🧠 **Contexto Activo:** Visualiza en vivo qué tecnologías, tests y estructura detecta la herramienta en tu PC.
*   🏷️ **Etiquetas (Pills):** Organiza tus prompts de forma visual y moderna.
*   ⚙️ **Configuración:** Ajusta rutas de bases de datos y filtros de seguridad.

---

## 📝 Estructura de Decisiones (ADR)
El proyecto mantiene registros estructurados (Architecture Decision Records) para asegurar el rigor arquitectónico:

- **ADR-0001: Git como almacenamiento:** Justificación del uso de Git para el versionado nativo de prompts.
- **ADR-0002: Estrategia de extracción de contexto:** Racional detrás de la detección automática de stacks.
- **ADR-0003: Implementación de búsqueda:** Diseño del sistema FTS con SQLite.
- **ADR-0004: Integración GUI con Backend:** Acoplamiento de la app visual a la lógica core (Git, FTS5, Jinja2).

### Estados Soportados:
- **Proposed:** La decisión está en fase de revisión.
- **Accepted:** La decisión ha sido aprobada e implementada.
- **Deprecated:** La decisión ya no es relevante.

## 📖 Documentación Adicional
- [🏛️ Arquitectura y Decisiones de Diseño](docs/ARCHITECTURE.md)
- [🚀 Ejemplos de Uso](docs/EXAMPLES.md)
- [🛠️ Solución de Problemas](docs/TROUBLESHOOTING.md)
- [🤝 Guía de Contribución](CONTRIBUTING.md)
- [⚖️ Código de Conducta](CODE_OF_CONDUCT.md)

## ⚖️ Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

Desarrollado con ❤️ por Robert Salinas para ingenieros que buscan elevar la calidad de sus interacciones con LLMs mediante el rigor técnico y el contexto.
