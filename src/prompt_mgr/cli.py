import typer
import os
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from .manager import PromptManager

app = typer.Typer(
    help="Context-Aware Prompt Manager - Gestiona tus prompts con contexto de proyecto."
)
console = Console()


def get_manager() -> PromptManager:
    """Obtiene una instancia de PromptManager para el directorio actual."""
    return PromptManager(os.getcwd())


@app.command()
def init() -> None:
    """Inicializa el gestor de prompts en el directorio actual."""
    mgr = get_manager()
    mgr.init_project()
    console.print(
        "[bold green]¡Éxito![/bold green] Proyecto inicializado correctamente."
    )


@app.command()
def add(
    name: str = typer.Argument(..., help="Nombre descriptivo del prompt"),
    template: str = typer.Argument(..., help="El template del prompt (soporta Jinja2)"),
    description: str = typer.Option(
        "Sin descripción", "--desc", "-d", help="Descripción detallada"
    ),
    tags: Optional[List[str]] = typer.Option(
        None, "--tag", "-t", help="Etiquetas para categorizar"
    ),
    filename: Optional[str] = typer.Option(
        None, "--file", "-f", help="Nombre de archivo específico"
    ),
) -> None:
    """Añade un nuevo prompt al sistema."""
    mgr = get_manager()
    if not filename:
        filename = name.lower().replace(" ", "_")

    data = {
        "name": name,
        "description": description,
        "template": template,
        "tags": tags or [],
        "version": "0.1.0",
    }

    try:
        path = mgr.add_prompt(filename, data)
        console.print(
            f"[bold green]Prompt añadido correctamente en:[/bold green] {path}"
        )
    except Exception as e:
        console.print(f"[bold red]Error al añadir prompt:[/bold red] {e}")


@app.command(name="list")
def list_prompts(
    tag: Optional[str] = typer.Option(None, help="Filtrar por etiqueta")
) -> None:
    """Lista todos los prompts disponibles."""
    mgr = get_manager()
    prompts = mgr.list_prompts(tag)

    if not prompts:
        console.print("No se encontraron prompts.")
        return

    table = Table(title="Prompts Disponibles")
    table.add_column("Archivo", style="cyan")
    table.add_column("Nombre", style="green")
    table.add_column("Etiquetas", style="magenta")
    table.add_column("Versión", style="yellow")

    for p in prompts:
        table.add_row(
            p["filename"],
            p["name"],
            ", ".join(p.get("tags", [])),
            p.get("version", "0.1.0"),
        )

    console.print(table)


@app.command()
def search(query: str = typer.Argument(..., help="Término de búsqueda")) -> None:
    """Busca prompts utilizando búsqueda de texto completo (FTS)."""
    mgr = get_manager()
    results = mgr.search_prompts(query)

    if not results:
        console.print(f"No se encontraron resultados para: {query}")
        return

    table = Table(title=f"Resultados de búsqueda para: {query}")
    table.add_column("Ruta", style="cyan")
    table.add_column("Nombre", style="green")
    table.add_column("Descripción", style="white")

    for r in results:
        table.add_row(r["path"], r["name"], r["description"])

    console.print(table)


@app.command()
def export(
    filename: str = typer.Argument(
        ..., help="Nombre del archivo del prompt a exportar"
    ),
    format: str = typer.Option(
        "yaml", "--format", help="Formato de salida (json, yaml, markdown)"
    ),
) -> None:
    """Exporta un prompt con el contexto del proyecto inyectado automáticamente."""
    mgr = get_manager()
    try:
        output = mgr.export_prompt(filename, format)
        console.print(output)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@app.command()
def diff(
    filename: str = typer.Argument(..., help="Nombre del archivo del prompt"),
    rev1: str = typer.Option("HEAD~1", help="Primera revisión (Git)"),
    rev2: str = typer.Option("HEAD", help="Segunda revisión (Git)"),
) -> None:
    """Muestra los cambios entre versiones de un prompt."""
    mgr = get_manager()
    try:
        diff_output = mgr.get_diff(filename, rev1, rev2)
        console.print(diff_output)
    except Exception as e:
        console.print(f"[bold red]Error al obtener diff:[/bold red] {e}")


@app.command()
def context() -> None:
    """Muestra el contexto del proyecto detectado automáticamente."""
    mgr = get_manager()
    ctx = mgr.analyzer.analyze()
    console.print_json(data=ctx)


if __name__ == "__main__":
    app()
