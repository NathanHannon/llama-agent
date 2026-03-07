import os
import re
import numpy as np
import typer
import pyfiglet
import importlib.util
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.theme import Theme
from rich.table import Table
from rich.color import Color
from llama_agent.agent import LlamaAgent

app = typer.Typer()

# High-Tech Inspired Colors (Blue to Cyan)
FUSION_BLUE = "#0081FB"
FUSION_PURPLE = "#7101FF"
FUSION_CYAN = "#00F2FE"

# Base Theme definitions
THEMES = {
    "fusion": Theme({
        "info": FUSION_CYAN,
        "warning": "yellow",
        "error": "bold red",
        "success": FUSION_BLUE,
        "brand": f"bold {FUSION_BLUE}",
        "user": f"bold {FUSION_CYAN}",
        "bot": f"bold {FUSION_PURPLE}",
    }),
    "matrix": Theme({
        "info": "green",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
        "brand": "bold green",
        "user": "green",
        "bot": "bold white",
    }),
    "classic": Theme({
        "info": "blue",
        "warning": "yellow",
        "error": "red",
        "success": "green",
        "brand": "bold blue",
        "user": "bold blue",
        "bot": "bold white",
    })
}

def load_external_themes():
    """Loads additional themes from themes.py if it exists."""
    themes_path = os.path.join(os.getcwd(), "themes.py")
    if not os.path.exists(themes_path):
        return
    
    try:
        spec = importlib.util.spec_from_file_location("themes", themes_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for variables ending in _THEME
        for attr in dir(module):
            if attr.endswith("_THEME"):
                theme_name = attr.replace("_THEME", "").lower()
                theme_obj = getattr(module, attr)
                if isinstance(theme_obj, Theme):
                    THEMES[theme_name] = theme_obj
    except Exception as e:
        # Silently fail if themes.py is broken
        pass

# Initialize external themes
load_external_themes()

# Global state for theme management
current_theme_name = "fusion"
console = Console(theme=THEMES[current_theme_name])


def hex_to_rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)])


def get_gradient_text(text, start_color, end_color):
    """Applies a horizontal gradient to ASCII art."""
    lines = text.splitlines()
    if not lines:
        return Text(text)
    
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    
    rendered_text = Text()
    for line in lines:
        for i, char in enumerate(line):
            mix = i / len(line) if len(line) > 1 else 0
            current_rgb = (1 - mix) * start_rgb + mix * end_rgb
            current_hex = "#{:02x}{:02x}{:02x}".format(int(current_rgb[0]), int(current_rgb[1]), int(current_rgb[2]))
            rendered_text.append(char, style=current_hex)
        rendered_text.append("\n")
    return rendered_text


def print_logo(theme_name):
    """Prints a clean LLAMA AGENT logo with a high-tech gradient."""
    llama_text = pyfiglet.figlet_format("LLAMA", font="block")
    agent_text = pyfiglet.figlet_format("AGENT  CLI", font="slant")

    if theme_name == "fusion":
        console.print(get_gradient_text(llama_text, FUSION_BLUE, FUSION_CYAN))
        console.print(Text(agent_text, style=f"bold {FUSION_CYAN}"))
    else:
        # Use info color for non-fusion themes
        brand_style = "bold white"
        if theme_name in THEMES:
            # Fallback style
            brand_style = "bold green" if theme_name == "matrix" else "bold blue"
            
        console.print(Text(llama_text, style=brand_style))
        console.print(Text(agent_text, style="bold white"))
    
    console.print("[dim]" + "━" * console.width + "[/]\n")


@app.command()
def start(
    model: str = typer.Option(None, help="Model ID to use."),
    theme: str = typer.Option("fusion", help="Initial theme (fusion, matrix, classic, emerald)"),
):
    """Starts the interactive Llama CLI with high-fidelity UI."""
    global console, current_theme_name
    
    # Reload to catch runtime changes
    load_external_themes()
    
    current_theme_name = theme if theme in THEMES else "fusion"
    console = Console(theme=THEMES[current_theme_name])

    print_logo(current_theme_name)
    
    welcome_message = f"""
[success]Connected to Llama Agentic Engine[/]
[info]Theme: {current_theme_name}[/] | Type [warning]/help[/] for command list.
[dim]An independent AI assistant powered by Llama weights.[/]
"""
    console.print(Panel(welcome_message.strip(), border_style=FUSION_BLUE))

    agent = LlamaAgent(model_id=model)

    while True:
        try:
            # Theme-specific prompt color
            user_style = "bold cyan"
            if current_theme_name == "fusion": user_style = f"bold {FUSION_CYAN}"
            elif current_theme_name == "matrix": user_style = "green"
            elif current_theme_name == "classic": user_style = "bold blue"
            elif current_theme_name == "emerald": user_style = "bold light_green"

            user_input = Prompt.ask(f"[{user_style}]YOU[/]")

            if not user_input.strip():
                continue

            if user_input.startswith("/"):
                cmd_parts = user_input.lower().strip().split()
                cmd = cmd_parts[0]
                
                if cmd in ["/exit", "/quit"]:
                    console.print("[warning]Shutting down agent. Goodbye![/]")
                    break
                
                elif cmd == "/theme":
                    if len(cmd_parts) > 1 and cmd_parts[1] in THEMES:
                        current_theme_name = cmd_parts[1]
                        console = Console(theme=THEMES[current_theme_name])
                        console.print(f"[success]Theme switched to {current_theme_name}![/]")
                    else:
                        console.print(f"[warning]Available themes: {', '.join(THEMES.keys())}[/]")
                    continue
                
                elif cmd == "/history":
                    table = Table(title="Conversation History", border_style="info")
                    table.add_column("Role", style="bold")
                    table.add_column("Content", overflow="fold")
                    for msg in agent.messages[1:]:
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")
                        if not content and hasattr(msg, "tool_calls"):
                            content = "[dim]Tool Call Execution[/]"
                        table.add_row(role, str(content)[:100] + "...")
                    console.print(table)
                    continue

                elif cmd == "/system":
                    console.print(Panel(agent.messages[0]["content"], title="System Prompt", border_style="info"))
                    continue

                elif cmd == "/clear":
                    agent.clear_history()
                    console.print("[success]History purged.[/]")
                    continue

                elif cmd == "/help":
                    help_table = Table(title="Commands", border_style=FUSION_BLUE)
                    help_table.add_column("Command", style="info")
                    help_table.add_column("Description")
                    help_table.add_row("/theme <name>", "Change UI theme")
                    help_table.add_row("/history", "View full message log")
                    help_table.add_row("/system", "Peek at agent's instructions")
                    help_table.add_row("/clear", "Reset conversation")
                    help_table.add_row("/exit", "Close application")
                    console.print(help_table)
                    continue

            with console.status(f"[{FUSION_BLUE}]Llama is reasoning..."):
                response = agent.chat(user_input)

            # Bot style lookup
            bot_style = "bold white"
            if current_theme_name == "fusion": bot_style = f"bold {FUSION_PURPLE}"
            elif current_theme_name == "matrix": bot_style = "bold white"
            elif current_theme_name == "emerald": bot_style = "bold green"
            
            console.print(f"\n[{bot_style}]LLAMA[/]")
            console.print(Markdown(response))
            console.print("-" * console.width, style="dim")
            
        except KeyboardInterrupt:
            console.print("\n[warning]Interrupted. Type /exit to close.[/]")
            continue


if __name__ == "__main__":
    app()
