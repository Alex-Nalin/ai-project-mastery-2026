from abc import ABC, abstractmethod
from typing import Dict, Any, List
import json

class ToolCallingProvider(ABC):
    @abstractmethod
    def format_tools(self, tools: List[Dict]) -> Any:
        pass
    
    @abstractmethod
    def parse_tool_calls(self, response: Any) -> List[Dict]:
        pass
    
    @abstractmethod
    def call_with_tools(self, prompt: str, tools: List[Dict]) -> Dict:
        pass

class OpenAIProvider(ToolCallingProvider):
    def __init__(self, api_key: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
    
    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": tool
            }
            for tool in tools
        ]
    
    def parse_tool_calls(self, response) -> List[Dict]:
        message = response.choices[0].message
        if not message.tool_calls:
            return []
        
        return [
            {
                "name": tc.function.name,
                "arguments": json.loads(tc.function.arguments),
                "id": tc.id
            }
            for tc in message.tool_calls
        ]
    
    def call_with_tools(self, prompt: str, tools: List[Dict]) -> Dict:
        response = self.client.chat.completions.create(
            model="gpt-5.5-2026-04-01",
            messages=[{"role": "user", "content": prompt}],
            tools=self.format_tools(tools)
        )
        
        tool_calls = self.parse_tool_calls(response)
        content = response.choices[0].message.content
        
        return {
            "content": content,
            "tool_calls": tool_calls
        }

class AnthropicProvider(ToolCallingProvider):
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        formatted = []
        for tool in tools:
            formatted.append({
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool["parameters"]
            })
        return formatted
    
    def parse_tool_calls(self, response) -> List[Dict]:
        tool_calls = []
        for content in response.content:
            if content.type == "tool_use":
                tool_calls.append({
                    "name": content.name,
                    "arguments": content.input,
                    "id": content.id
                })
        return tool_calls
    
    def call_with_tools(self, prompt: str, tools: List[Dict]) -> Dict:
        response = self.client.messages.create(
            model="claude-opus-4-8-2026-04-15",
            max_tokens=4096,
            tools=self.format_tools(tools),
            messages=[{"role": "user", "content": prompt}]
        )
        
        tool_calls = self.parse_tool_calls(response)
        content = ""
        for block in response.content:
            if block.type == "text":
                content = block.text
        
        return {
            "content": content,
            "tool_calls": tool_calls
        }

class GeminiProvider(ToolCallingProvider):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.5-pro-001')
    
    def format_tools(self, tools: List[Dict]) -> List[genai.protos.Tool]:
        import google.generativeai as genai
        
        declarations = []
        for tool in tools:
            params = tool["parameters"]
            properties = {}
            for key, value in params.get("properties", {}).items():
                schema_type = genai.protos.Type.STRING
                if value.get("type") == "integer":
                    schema_type = genai.protos.Type.INTEGER
                elif value.get("type") == "number":
                    schema_type = genai.protos.Type.NUMBER
                elif value.get("type") == "boolean":
                    schema_type = genai.protos.Type.BOOLEAN
                elif value.get("type") == "array":
                    schema_type = genai.protos.Type.ARRAY
                
                properties[key] = genai.protos.Schema(
                    type=schema_type,
                    description=value.get("description", ""),
                    enum=value.get("enum", [])
                )
            
            declarations.append(
                genai.protos.FunctionDeclaration(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties=properties,
                        required=params.get("required", [])
                    )
                )
            )
        
        return [genai.protos.Tool(function_declarations=declarations)]
    
    def parse_tool_calls(self, response) -> List[Dict]:
        tool_calls = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    tool_calls.append({
                        "name": part.function_call.name,
                        "arguments": dict(part.function_call.args),
                        "id": part.function_call.name
                    })
        return tool_calls
    
    def call_with_tools(self, prompt: str, tools: List[Dict]) -> Dict:
        response = self.model.generate_content(
            prompt,
            tools=self.format_tools(tools)
        )
        
        tool_calls = self.parse_tool_calls(response)
        content = response.text if hasattr(response, 'text') else ""
        
        return {
            "content": content,
            "tool_calls": tool_calls
        }

# Usage
provider = OpenAIProvider(api_key="your-key")
result = provider.call_with_tools(
    "What's the weather in Tokyo?",
    [
        {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    ]
)

if result["tool_calls"]:
    for tc in result["tool_calls"]:
        print(f"Calling {tc['name']} with {tc['arguments']}")
