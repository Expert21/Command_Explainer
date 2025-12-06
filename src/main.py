"""
Command Explainer CLI - Main entry point.
Terminal command generator and explainer powered by Ollama.
"""

import asyncio
import sys
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.live import Live

from src.core.engine import CommandEngine, Persona
from src.core.ollama_client import OllamaError, OllamaConnectionError, OllamaModelNotFoundError
from src.config.settings import get_settings
from src import __version__


console = Console()


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_command(command: str):
    """Print a generated command."""
    console.print(Panel(
        Text(command, style="bold cyan"),
        title="[bold]Generated Command[/bold]",
        border_style="cyan"
    ))


async def stream_response(generator, title: str = "Response"):
    """Stream and display a response from the LLM."""
    full_response = ""
    
    console.print(f"\n[bold]{title}:[/bold]")
    console.print()
    
    try:
        async for chunk in generator:
            console.print(chunk, end="")
            full_response += chunk
    except Exception as e:
        print_error(f"Stream interrupted: {e}")
    
    console.print("\n")
    return full_response


async def run_interactive(persona: str):
    """Run interactive mode."""
    settings = get_settings()
    
    persona_enum = Persona(persona) if persona else Persona(settings.get_persona())
    
    engine = CommandEngine(persona=persona_enum)
    
    # Check connection first
    if not await engine.check_connection():
        print_error("Cannot connect to Ollama. Make sure it's running!")
        print_error(f"Expected at: {settings.ollama.host}")
        await engine.close()
        return
    
    console.print(Panel(
        f"[bold cyan]Command Explainer[/bold cyan] v{__version__}\n\n"
        f"Model: [yellow]{settings.get_model()}[/yellow]\n"
        f"Persona: [green]{persona_enum.value}[/green]\n\n"
        "[dim]Type your request, or:[/dim]\n"
        "  • [bold]/generate[/bold] <description> - Generate a command\n"
        "  • [bold]/explain[/bold] <command> - Explain a command\n"
        "  • [bold]/persona[/bold] <general|security> - Switch persona\n"
        "  • [bold]/quit[/bold] or [bold]exit[/bold] - Exit",
        title="[bold]Interactive Mode[/bold]",
        border_style="blue"
    ))
    
    try:
        while True:
            try:
                user_input = Prompt.ask("\n[bold blue]>[/bold blue]")
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Goodbye![/dim]")
                break
            
            if not user_input.strip():
                continue
            
            # Handle commands
            if user_input.lower() in ("/quit", "exit", "quit", "/exit"):
                console.print("[dim]Goodbye![/dim]")
                break
            
            if user_input.startswith("/generate "):
                description = user_input[10:].strip()
                if description:
                    try:
                        result = await engine.generate(description, stream=False)
                        print_command(result)
                    except OllamaError as e:
                        print_error(str(e))
                continue
            
            if user_input.startswith("/explain "):
                command = user_input[9:].strip()
                if command:
                    try:
                        generator = await engine.explain(command, stream=True)
                        await stream_response(generator, "Explanation")
                    except OllamaError as e:
                        print_error(str(e))
                continue
            
            if user_input.startswith("/persona "):
                new_persona = user_input[9:].strip().lower()
                if new_persona in ("general", "security"):
                    engine.set_persona(Persona(new_persona))
                    print_success(f"Switched to {new_persona} persona")
                else:
                    print_error("Available personas: general, security")
                continue
            
            # Default: chat mode
            try:
                generator = await engine.chat(user_input, stream=True)
                await stream_response(generator, "Assistant")
            except OllamaError as e:
                print_error(str(e))
    
    finally:
        await engine.close()


@click.group(invoke_without_command=True)
@click.option("--persona", "-p", type=click.Choice(["general", "security"]), 
              help="Set the assistant persona")
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx, persona, version):
    """
    Command Explainer - Generate and explain terminal commands using AI.
    
    Run without arguments to enter interactive mode.
    """
    if version:
        console.print(f"cmdex version {__version__}")
        return
    
    # If no subcommand, run interactive mode
    if ctx.invoked_subcommand is None:
        asyncio.run(run_interactive(persona))


@cli.command()
@click.argument("description")
@click.option("--persona", "-p", type=click.Choice(["general", "security"]),
              help="Set the assistant persona")
def generate(description: str, persona: str):
    """Generate a terminal command from a natural language description."""
    async def _generate():
        settings = get_settings()
        persona_enum = Persona(persona) if persona else Persona(settings.get_persona())
        engine = CommandEngine(persona=persona_enum)
        
        try:
            if not await engine.check_connection():
                print_error("Cannot connect to Ollama. Is it running?")
                return
            
            with console.status("[bold blue]Generating command...[/bold blue]"):
                result = await engine.generate(description, stream=False)
            
            print_command(result.strip())
            
        except OllamaConnectionError as e:
            print_error(str(e))
        except OllamaModelNotFoundError as e:
            print_error(str(e))
        except OllamaError as e:
            print_error(f"Ollama error: {e}")
        finally:
            await engine.close()
    
    asyncio.run(_generate())


@cli.command()
@click.argument("command")
@click.option("--persona", "-p", type=click.Choice(["general", "security"]),
              help="Set the assistant persona")
def explain(command: str, persona: str):
    """Explain what a terminal command does."""
    async def _explain():
        settings = get_settings()
        persona_enum = Persona(persona) if persona else Persona(settings.get_persona())
        engine = CommandEngine(persona=persona_enum)
        
        try:
            if not await engine.check_connection():
                print_error("Cannot connect to Ollama. Is it running?")
                return
            
            generator = await engine.explain(command, stream=True)
            await stream_response(generator, "Explanation")
            
        except OllamaConnectionError as e:
            print_error(str(e))
        except OllamaModelNotFoundError as e:
            print_error(str(e))
        except OllamaError as e:
            print_error(f"Ollama error: {e}")
        finally:
            await engine.close()
    
    asyncio.run(_explain())


@cli.group()
def models():
    """Manage Ollama models."""
    pass


@models.command("list")
def list_models():
    """List available Ollama models."""
    async def _list():
        engine = CommandEngine()
        
        try:
            if not await engine.check_connection():
                print_error("Cannot connect to Ollama. Is it running?")
                return
            
            models_list = await engine.list_models()
            
            if not models_list:
                console.print("[yellow]No models found. Run 'ollama pull <model>' to download one.[/yellow]")
                return
            
            console.print("\n[bold]Available Models:[/bold]\n")
            
            for model in models_list:
                name = model.get("name", "unknown")
                size = model.get("size", 0)
                size_gb = size / (1024 ** 3)
                console.print(f"  • [cyan]{name}[/cyan] ({size_gb:.1f} GB)")
            
            console.print()
            
        except OllamaError as e:
            print_error(str(e))
        finally:
            await engine.close()
    
    asyncio.run(_list())


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
