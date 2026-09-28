# ADR 0005: Separar biblioteca y proyecto activo

**Estado:** Accepted  
**Fecha:** 2026-09-27

La versión anterior usaba el directorio de ejecución como biblioteca, contexto e historial Git. Esto podía añadir prompts y commits al repositorio que el usuario solo quería analizar.

La GUI mantiene ahora la biblioteca en `%APPDATA%\RS-Prompt-Manager\library` y trata el proyecto activo como entrada de solo lectura. El versionado es opcional y afecta exclusivamente a la biblioteca. La CLI conserva su comportamiento basado en el directorio actual para compatibilidad.

Esta decisión hace explícito el límite de datos, evita efectos laterales y permite distribuir un ejecutable independiente.
