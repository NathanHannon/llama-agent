import os
import subprocess

def list_files(directory="."):
    """Lists files in the specified directory."""
    try:
        return "
".join(os.listdir(directory))
    except Exception as e:
        return f"Error: {e}"

def read_file(file_path):
    """Reads the content of a file."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def run_shell(command):
    """Executes a shell command (dangerous, use with caution!)."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        return f"Stdout: {result.stdout}
Stderr: {result.stderr}"
    except Exception as e:
        return f"Error: {e}"

# Metadata for tool-calling
AVAILABLE_TOOLS = {
    "list_files": list_files,
    "read_file": read_file,
    "run_shell": run_shell,
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Lists the files in the current or a specific directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "The path to the directory."}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a specific file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "The path to the file."}
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Executes a shell command on the host system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command to run."}
                },
                "required": ["command"],
            },
        },
    },
]
