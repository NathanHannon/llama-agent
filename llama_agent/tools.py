import os
import subprocess
import requests
from llama_agent.skills import scan_skills


def list_files(directory="."):
    """Lists files in the specified directory."""
    try:
        files = os.listdir(directory)
        return "\n".join(files) if files else "Directory is empty."
    except Exception as e:
        return f"Error listing files: {e}"


def get_tree(directory=".", max_depth=2):
    """Provides a recursive tree view of the directory structure."""
    try:
        tree = []
        for root, dirs, files in os.walk(directory):
            level = root.replace(directory, "").count(os.sep)
            if level > max_depth:
                continue
            indent = " " * 4 * level
            tree.append(f"{indent}{os.path.basename(root)}/")
            sub_indent = " " * 4 * (level + 1)
            for f in files:
                tree.append(f"{sub_indent}{f}")
        return "\n".join(tree)
    except Exception as e:
        return f"Error generating tree: {e}"


def read_file(file_path):
    """Reads the content of a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {e}"


def write_file(file_path, content):
    """Writes the complete content to a file. MUST provide file_path and content."""
    try:
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {e}"


def replace_text(file_path, old_string, new_string):
    """Replaces old_string with new_string in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if old_string not in content:
            return f"Error: The target text was not found in {file_path}."
        new_content = content.replace(old_string, new_string)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return f"Successfully updated {file_path}"
    except Exception as e:
        return f"Error replacing text in {file_path}: {e}"


def grep_search(pattern, directory="."):
    """Searches for a text pattern in a directory."""
    try:
        if os.name == 'nt':
            cmd = f'findstr /S /N /I /C:"{pattern}" "{directory}\\*"'
        else:
            cmd = f'grep -rnEi "{pattern}" "{directory}" --exclude-dir=.git --exclude-dir=venv'
            
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout[:5000] if result.stdout else "No matches found."
    except Exception as e:
        return f"Error searching: {e}"


def web_fetch(url):
    """Fetches text from a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        import re
        text = re.sub('<[^<]+?>', '', response.text)
        return text[:10000]
    except Exception as e:
        return f"Error fetching URL: {e}"


def git_info():
    """Returns git status."""
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
        return f"On branch: {branch}"
    except Exception as e:
        return "Not a git repository."


def run_shell(command, input_text=None):
    """Executes a shell command."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, 
            input=input_text + "\n" if input_text else None, timeout=30
        )
        return f"Exit Code {result.returncode}\nStdout: {result.stdout}\nStderr: {result.stderr}"
    except Exception as e:
        return f"Error running command: {e}"


def check_syntax(file_path):
    """Checks if a Python file has valid syntax without running it."""
    try:
        import py_compile
        py_compile.compile(file_path, doraise=True)
        return f"Syntax check passed for {file_path}"
    except Exception as e:
        return f"Syntax Error in {file_path}: {str(e)}"


def run_tests():
    """Autodetects project type and runs the appropriate test suite."""
    try:
        # 1. Check for Python (pytest)
        if os.path.exists("pytest.ini") or os.path.exists("tests") or any(f.endswith(".py") for f in os.listdir(".")):
            # Try pytest first, fallback to unittest
            try:
                res = subprocess.run(["pytest", "--version"], capture_output=True)
                if res.returncode == 0:
                    cmd = "pytest"
                else:
                    cmd = "python -m unittest discover"
            except:
                cmd = "python -m unittest discover"
        
        # 2. Check for Node.js
        elif os.path.exists("package.json"):
            cmd = "npm test"
            
        # 3. Check for Rust
        elif os.path.exists("Cargo.toml"):
            cmd = "cargo test"
            
        else:
            return "Error: Could not autodetect project type for testing."

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return f"Test Results ({cmd}):\nExit Code {result.returncode}\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        return f"Error running tests: {e}"


def remember_fact(fact):
    """Saves a fact to memory."""
    try:
        path = os.path.expanduser("~/.llama_agent/memory.txt")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"- {fact}\n")
        return f"Remembered: {fact}"
    except Exception as e:
        return f"Error: {e}"


def get_memories():
    """Reads all memories."""
    try:
        path = os.path.expanduser("~/.llama_agent/memory.txt")
        if not os.path.exists(path): return "No memories yet."
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


# --- TOOL DEFINITIONS ---
AVAILABLE_TOOLS = {
    "list_files": list_files,
    "get_tree": get_tree,
    "read_file": read_file,
    "write_file": write_file,
    "replace_text": replace_text,
    "grep_search": grep_search,
    "web_fetch": web_fetch,
    "git_info": git_info,
    "run_shell": run_shell,
    "check_syntax": check_syntax,
    "run_tests": run_tests,
    "remember_fact": remember_fact,
    "get_memories": get_memories,
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_tree",
            "description": "recursive tree view of the directory",
            "parameters": {"type": "object", "properties": {"directory": {"type": "string"}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "read contents of a file",
            "parameters": {
                "type": "object", 
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "create or overwrite a file. MUST specify file_path and content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "exact path to save the file"},
                    "content": {"type": "string", "description": "full content of the file"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "run a shell command. provide input_text if prompted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "input_text": {"type": "string"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_syntax",
            "description": "Verify that a Python file has no syntax errors.",
            "parameters": {
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Autodetect project type and run all tests."
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "search for text in the project",
            "parameters": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}},
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remember_fact",
            "description": "save a user preference",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string"}},
                "required": ["fact"]
            }
        }
    },
    {
        "type": "function",
        "function": {"name": "get_memories", "description": "retrieve saved facts"}
    }
]
