# ADR 0001: Git como almacenamiento y versionado

## Estatus
Aceptado

## Contexto
Necesitamos una forma de rastrear cambios en los prompts, permitir reversiones y colaboración entre múltiples usuarios.

## Decisión
Utilizar Git como el motor de almacenamiento principal para los archivos de prompts (YAML). Cada acción de escritura en el CLI resultará en un commit automático.

## Consecuencias
- **Pros:** Versionado nativo, diffs fáciles, historial completo, integración con flujos de trabajo existentes.
- **Contras:** Dependencia de Git en el sistema del usuario.
