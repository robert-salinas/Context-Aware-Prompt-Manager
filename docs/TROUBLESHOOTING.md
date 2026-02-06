# Solución de Problemas (Troubleshooting)

## 1. Error: `attempted relative import with no known parent package`
Este error suele ocurrir al intentar ejecutar el script de CLI directamente con `python src/prompt_mgr/cli.py`.
**Solución:**
Ejecuta el módulo usando `-m` y asegúrate de que `src` esté en tu `PYTHONPATH`:
```bash
$env:PYTHONPATH="src"
python -m prompt_mgr.cli <comando>
```
O mejor aún, instala el paquete en modo editable:
```bash
pip install -e .
prompt-mgr <comando>
```

## 2. Los cambios no se ven reflejados en Git
CAPM intenta hacer commit automáticamente de cada prompt añadido. Si falla:
**Solución:**
- Verifica que tienes `git` instalado en tu PATH.
- Asegúrate de haber ejecutado `prompt-mgr init` primero.
- Revisa los permisos de escritura en la carpeta `prompts/`.

## 3. La búsqueda no encuentra prompts nuevos
Si la base de datos de búsqueda parece desactualizada.
**Solución:**
- Elimina el archivo `.prompt_mgr.db` y vuelve a añadir los prompts.
- Asegúrate de que los archivos en `prompts/` tengan extensión `.yaml`.

## 4. Error de Jinja2: `UndefinedError`
Ocurre si usas una variable en el template que no está disponible en el contexto.
**Solución:**
- Ejecuta `prompt-mgr context` para ver qué variables están disponibles actualmente.
- Asegúrate de que los nombres de las variables coincidan exactamente (e.g., `project_name` no `projectName`).
