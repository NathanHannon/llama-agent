import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from llama_agent.tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS, get_tree
from llama_agent.skills import scan_skills

load_dotenv()


class LlamaAgent:
    def __init__(self, model_id: str = None):
        provider = os.getenv("AI_PROVIDER", "groq").lower()
        if provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1"
            self.api_key = os.getenv("GROQ_API_KEY")
        elif provider == "openrouter":
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = os.getenv("OPENROUTER_API_KEY")
        elif provider == "ollama":
            self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
            self.api_key = "ollama"
        elif provider == "lmstudio":
            self.base_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
            self.api_key = "lm-studio"
        else:
            raise ValueError(f"Unknown AI_PROVIDER: '{provider}'")

        self.model = model_id or os.getenv("AI_MODEL", "llama-3.3-70b-versatile")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

        # Pre-load project structure into context
        self.project_tree = get_tree(".", max_depth=3)

        self.skills = scan_skills()
        skills_text = ""
        if self.skills:
            skills_text = "\n\nAvailable Agent Skills:\n"
            for name, meta in self.skills.items():
                skills_text += f"- {name}: {meta['description']}\n"

        self.system_prompt = {
            "role": "system",
            "content": (
                "You are an expert autonomous software engineer. "
                "You have access to tools to read, write, and search code. "
                f"\n\nCURRENT PROJECT STRUCTURE:\n{self.project_tree}\n"
                "\nCRITICAL RULES:\n"
                "1. **Action Oriented**: If you claim to do something (like 'I will create themes.py'), you MUST use the corresponding tool immediately.\n"
                "2. **Path Accuracy**: Always use the exact file paths shown in the project structure above.\n"
                "3. **Required Arguments**: You MUST provide all arguments defined in the tool schema.\n"
                "4. **No Hallucinations**: Do not report success until a tool actually returns a success message."
                + skills_text
            ),
        }
        self.messages = [self.system_prompt]

    def clear_history(self):
        self.messages = [self.system_prompt]

    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})

        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                )
            except Exception as e:
                # If tool-calling fails, we try a non-tool recovery turn
                if "400" in str(e):
                    return "⚠️ Groq Tool-Calling Error. I'll try to provide a text-only response or you can try rephrasing."
                return f"⚠️ API Error: {str(e)}"

            response_message = response.choices[0].message
            self.messages.append(response_message)

            # Check if there are tool calls
            if not response_message.tool_calls:
                return response_message.content or "Task completed."

            # Process all requested tool calls in parallel
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                
                if function_name not in AVAILABLE_TOOLS:
                    tool_output = f"Error: Tool '{function_name}' not found."
                else:
                    function_to_call = AVAILABLE_TOOLS[function_name]
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        tool_output = function_to_call(**function_args)
                    except Exception as e:
                        tool_output = f"Error executing tool: {str(e)}. Ensure you provided all required arguments."

                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(tool_output),
                    }
                )
            
            # Continue the loop to let the model react to the tool outputs
