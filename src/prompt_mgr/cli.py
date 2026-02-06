import typer
import os
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from .manager import PromptManager

app = typer.Typer(help="Context-Aware Prompt Manager")
console = Console()

def get_manager() -> PromptManager:
    return PromptManager(os.getcwd())

@app.command()
def init():
    """Initialize the prompt manager in the current directory."""
    mgr = get_manager()
    mgr.init_project()
    console.print("[bold green]Success![/bold green] Project initialized.")

@app.command()
def add(
    name: str = typer.Argument(..., help="Name of the prompt"),
    template: str = typer.Argument(..., help="The prompt template"),
    description: str = typer.Option("No description", "--desc", "-d", help="Prompt description"),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags for the prompt"),
    filename: Optional[str] = typer.Option(None, "--file", "-f", help="Specific filename")
):
    """Add a new prompt."""
    mgr = get_manager()
    if not filename:
        filename = name.lower().replace(" ", "_")
        
    data = {
        "name": name,
        "description": description,
        "template": template,
        "tags": tags or [],
        "version": "0.1.0"
    }
    
    try:
        path = mgr.add_prompt(filename, data)
        console.print(f"[bold green]Prompt added:[/bold green] {path}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command(name="list")
def list_prompts(tag: Optional[str] = typer.Option(None, help="Filter by tag")):
    """List all available prompts."""
    mgr = get_manager()
    prompts = mgr.list_prompts(tag)
    
    if not prompts:
        console.print("No prompts found.")
        return
        
    table = Table(title="Available Prompts")
    table.add_column("Filename", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Tags", style="magenta")
    table.add_column("Version", style="yellow")
    
    for p in prompts:
        table.add_row(
            p["filename"],
            p["name"],
            ", ".join(p.get("tags", [])),
            p.get("version", "0.1.0")
        )
        
    console.print(table)

@app.command()
def search(query: str = typer.Argument(..., help="Search query")):
    """Search for prompts using full-text search."""
    mgr = get_manager()
    results = mgr.search_prompts(query)
    
    if not results:
        console.print("No results found.")
        return
        
    table = Table(title=f"Search Results for: {query}")
    table.add_column("Path", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    
    for r in results:
        table.add_row(r["path"], r["name"], r["description"])
        
    console.print(table)

@app.command()
def export(
    filename: str = typer.Argument(..., help="Filename of the prompt to export"),
    format: str = typer.Option("yaml", "--format", help="Output format (json, yaml, markdown)")
):
    """Export a prompt with project context automatically filled."""
    mgr = get_manager()
    try:
        output = mgr.export_prompt(filename, format)
        console.print(output)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def diff(
    filename: str = typer.Argument(..., help="Filename of the prompt"),
    rev1: str = typer.Option("HEAD~1", help="First revision"),
    rev2: str = typer.Option("HEAD", help="Second revision")
):
    """Show changes between versions of a prompt."""
    mgr = get_manager()
    try:
        diff_output = mgr.get_diff(filename, rev1, rev2)
        console.print(diff_output)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def context():
    """Show the automatically detected project context."""
    mgr = get_manager()
    ctx = mgr.analyzer.analyze()
    console.print_json(data=ctx)

if __name__ == "__main__":
    app()
