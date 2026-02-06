# Ejemplos de Uso - Context-Aware Prompt Manager

Aquí encontrarás ejemplos prácticos de cómo aprovechar CAPM en diferentes tipos de proyectos.

## 1. Prompt para Refactorización (Python)

**Template:**
```yaml
name: "Python Refactor"
description: "Optimiza código Python siguiendo PEP8"
template: |
  Actúa como un experto en {{ tech_stack | join(' y ') }}.
  Estamos trabajando en {{ project_name }}.
  
  Por favor, refactoriza el siguiente código para hacerlo más legible y eficiente:
  {{ user_code }}
tags: ["python", "refactor"]
```

**Comando:**
```bash
prompt-mgr add "Python Refactor" "..." --tag "refactor"
```

## 2. Prompt para Documentación Automática

**Template:**
```yaml
name: "Doc Generator"
description: "Genera docstrings para funciones"
template: |
  Analiza la estructura de este proyecto: {{ structure }}.
  Basado en esto, genera docstrings detallados para la siguiente función en {{ tech_stack[0] }}:
  {{ function_code }}
tags: ["docs"]
```

## 3. Uso de Variables de Contexto

CAPM inyecta automáticamente las siguientes variables en tus prompts:

- `{{ project_name }}`: Nombre de la carpeta raíz.
- `{{ tech_stack }}`: Lista de lenguajes/frameworks detectados (e.g., `['Python', 'Node.js']`).
- `{{ readme_summary }}`: Primeros 500 caracteres de tu README.md.
- `{{ structure }}`: Resumen de directorios y archivos.

## 4. Exportación a diferentes formatos

```bash
# Markdown (Ideal para copiar a ChatGPT/Claude)
prompt-mgr export welcome.yaml --format markdown

# JSON (Para integraciones con scripts)
prompt-mgr export welcome.yaml --format json
```
