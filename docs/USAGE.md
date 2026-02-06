# Guía de Uso

## Instalación
```bash
pip install .
```

## Comandos Básicos

### Inicializar el gestor
```bash
prompt-mgr init
```

### Añadir un prompt
```bash
prompt-mgr add "Refactorizar código" "Ayúdame a refactorizar este archivo Python en el proyecto {{ project_name }}" --tag "refactoring" --desc "Prompt para limpieza de código"
```

### Listar prompts
```bash
prompt-mgr list
prompt-mgr list --tag "refactoring"
```

### Buscar prompts
```bash
prompt-mgr search "refactorizar"
```

### Exportar con contexto
```bash
prompt-mgr export refactorizar_codigo.yaml --format markdown
```

### Ver contexto detectado
```bash
prompt-mgr context
```

### Ver cambios (Diff)
```bash
prompt-mgr diff refactorizar_codigo.yaml
```
