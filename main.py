import typer
from rich.console import Console
from rich.markdown import Markdown
from agent import LlamaAgent

app = typer.Typer()
console = Console()

@app.command()
def start():
    """Starts the interactive Llama CLI."""
    agent = LlamaAgent()
    console.print("[bold green]Llama Agent Started![/] (Type 'exit' to quit)")
    
    while True:
        user_input = console.input("[bold blue]You:[/] ")
        if user_input.lower() in ["exit", "quit", "/q"]:
            console.print("[yellow]Goodbye![/]")
            break
            
        with console.status("[bold green]Llama is thinking..."):
            response = agent.chat(user_input)
        
        console.print(Markdown(response))

if __name__ == "__main__":
    app()
