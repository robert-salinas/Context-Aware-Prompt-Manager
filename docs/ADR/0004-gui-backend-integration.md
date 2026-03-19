# ADR 0004: Integración de la GUI con el Backend

## Estatus
Aceptado

## Contexto
La interfaz gráfica (GUI) inicial se desarrolló de forma desacoplada, gestionando sus propios datos en un archivo estático `prompts.json`. Al hacerlo, se estaban perdiendo las capacidades clave del backend como el control de versiones con Git, la búsqueda avanzada con FTS5 de SQLite y el renderizado automático de variables Jinja2.

## Decisión
Refactorizar la aplicación visual (`src/prompt_mgr/gui.py`) para que instancie y consuma la lógica de la clase `PromptManager` como su único origen de verdad. 

Esto implica:
1. **Migración de Datos:** Guardar y listar prompts desde archivos `.yaml` bajo el esquema del backend, disparando commits automáticos en Git por cada cambio.
2. **Consultas FTS5:** Delegar el filtrado de la barra de búsqueda al motor de base de datos del backend para escalabilidad.
3. **Variables Dinámicas:** Reemplazar la sintaxis de corchetes `[VARIABLE]` por el estándar Jinja2 `{{ variable }}` para mayor potencia templating.

## Consecuencias
- **Pros:** 
    - Unificación de la arquitectura.
    - Acceso a auditoría en Git de forma nativa desde la app.
    - Soporte para plantillas complejas.
- **Contras:** 
    - Mayor dependencia del entorno Python y Git por parte de la GUI (mitigado con un launcher automático).
