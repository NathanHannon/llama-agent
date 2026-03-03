import os
import typer
import pyfiglet
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from llama_agent.agent import LlamaAgent

app = typer.Typer()
console = Console()

MODELS = {
    "groq": [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
    ],
    "openrouter": [
        "meta-llama/llama-3.3-70b-instruct",
        "meta-llama/llama-3.1-405b",
        "meta-llama/llama-3.1-70b-instruct",
    ],
    "ollama": [
        "llama3.3",
        "llama3.1",
        "llama3",
        "mistral",
    ],
    "lmstudio": [
        "local-model",
    ],
}


def get_model_choice():
    """Interactive model picker."""
    provider = os.getenv("AI_PROVIDER", "groq")
    available_models = MODELS.get(provider, [])

    console.print(f"\n[bold cyan]Select a model for provider: {provider}[/]")
    for idx, model in enumerate(available_models, 1):
        console.print(f"[bold green]{idx}.[/] {model}")
    console.print(f"[bold green]{len(available_models) + 1}.[/] Custom / Other")

    choice = Prompt.ask(
        "\nChoose a number",
        choices=[str(i) for i in range(1, len(available_models) + 2)],
        default="1",
    )

    if int(choice) <= len(available_models):
        return available_models[int(choice) - 1]

    return Prompt.ask("Enter custom model ID")


@app.command()
def start(
    model: str = typer.Option(
        None, help="Model ID to use. Set to 'pick' to choose interactively."
    ),
):
    """Starts the interactive Llama CLI."""
    # Generate ASCII art logo
    llama_art = pyfiglet.figlet_format("Llama Agent", font="slant")

    # Create a gradient effect manually (simple version)
    logo_text = Text(llama_art, style="bold blue")

    # Add a welcome panel
    welcome_message = """
[bold green]Powered by Meta Llama 3 & 4[/]
Type [bold cyan]/help[/] for commands or just start chatting.
[dim]Press Ctrl+C to exit.[/]
"""

    console.print(logo_text)
    console.print(
        Panel(
            welcome_message.strip(),
            title="🦙 AI Coding Assistant",
            border_style="green",
        )
    )

    if model == "pick":
        model = get_model_choice()
        console.print(f"[dim]Selected model: {model}[/dim]\n")

    agent = LlamaAgent(model_id=model)

    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/]")
            
            if not user_input.strip():
                continue

            # Command handling
            if user_input.startswith("/"):
                cmd = user_input.lower().strip()
                if cmd in ["/exit", "/quit", "/q"]:
                    console.print("[yellow]Goodbye![/]")
                    break
                elif cmd in ["/help", "/h", "?"]:
                    help_text = """
[bold cyan]Available Commands:[/bold cyan]
- [bold green]/clear[/]: Clear conversation history
- [bold green]/skills[/]: List available agent skills
- [bold green]/model[/]: Show current model
- [bold green]/exit[/], [bold green]/quit[/]: Exit the application
- [bold green]/help[/]: Show this help message
"""
                    console.print(Panel(help_text.strip(), title="Help", border_style="cyan"))
                    continue
                elif cmd == "/clear":
                    agent.clear_history()
                    console.print("[yellow]Conversation history cleared![/]")
                    continue
                elif cmd == "/skills":
                    if not agent.skills:
                        console.print("[yellow]No skills found in ~/.agents/skills[/]")
                    else:
                        skill_list = "\n".join([f"- [bold]{name}[/]: {meta['description']}" for name, meta in agent.skills.items()])
                        console.print(Panel(skill_list, title="Available Skills", border_style="magenta"))
                    continue
                elif cmd == "/model":
                    console.print(f"[bold cyan]Current Model:[/bold cyan] {agent.model}")
                    continue
                
            with console.status("[bold green]Llama is thinking..."):
                response = agent.chat(user_input)
            
            console.print(Markdown(response))
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/]")
            break

if __name__ == "__main__":
    app()
