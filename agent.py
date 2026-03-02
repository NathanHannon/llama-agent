import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import AVAILABLE_TOOLS, TOOL_DEFINITIONS

load_dotenv()

class LlamaAgent:
    def __init__(self):
        provider = os.getenv("AI_PROVIDER", "groq")
        if provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1"
            self.api_key = os.getenv("GROQ_API_KEY")
        else:
            self.base_url = "https://openrouter.ai/api/v1"
            self.api_key = os.getenv("OPENROUTER_API_KEY")

        self.model = os.getenv("AI_MODEL", "llama-3.1-70b-versatile")
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        self.messages = [
            {"role": "system", "content": "You are a professional software engineering assistant. You can read files and run shell commands to help the user. If a tool returns an error, try to fix the issue or explain why it failed."}
        ]

    def chat(self, user_input):
        self.messages.append({"role": "user", "content": user_input})
        
        # Initial response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        self.messages.append(response_message)

        # Handle tool calls if the model wants to use a tool
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_to_call = AVAILABLE_TOOLS[function_name]
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                tool_output = function_to_call(**function_args)
                
                # Provide tool output back to the model
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_output,
                })
            
            # Get the final response after tool execution
            second_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )
            final_content = second_response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": final_content})
            return final_content

        return response_message.content
