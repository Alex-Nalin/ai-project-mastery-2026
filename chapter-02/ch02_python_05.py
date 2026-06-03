import json
from typing import List, Dict, Any
from openai import OpenAI

class ReActAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []
        
    def define_tools(self):
        """Define available tools for the agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_database",
                    "description": "Search the customer database for information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "table": {
                                "type": "string",
                                "enum": ["customers", "orders", "products"],
                                "description": "Which table to search"
                            }
                        },
                        "required": ["query", "table"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_refund",
                    "description": "Calculate refund amount for an order",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_id": {
                                "type": "string",
                                "description": "The order ID"
                            },
                            "reason": {
                                "type": "string",
                                "enum": ["damaged", "wrong_item", "changed_mind"],
                                "description": "Reason for refund"
                            }
                        },
                        "required": ["order_id", "reason"]
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_call: Dict) -> str:
        """Execute a tool and return the observation."""
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        if function_name == "search_database":
            # Simulate database search
            return json.dumps({
                "status": "success",
                "results": [
                    {"id": "ORD-12345", "customer": "Alice", "amount": 299.99, "status": "delivered"},
                    {"id": "ORD-12346", "customer": "Bob", "amount": 149.99, "status": "shipped"}
                ]
            })
        elif function_name == "calculate_refund":
            # Simulate refund calculation
            return json.dumps({
                "status": "success",
                "refund_amount": 299.99,
                "processing_fee": 0,
                "total_refund": 299.99
            })
        
        return json.dumps({"status": "error", "message": "Unknown tool"})
    
    def run(self, user_input: str, max_steps: int = 5):
        """Run the ReAct loop."""
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        for step in range(max_steps):
            response = self.client.chat.completions.create(
                model="gpt-5.5-2026-04-01",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a ReAct agent. Follow this loop:
1. REASON: Think about what information you need and what action to take
2. ACT: Call a function to get information
3. OBSERVE: Wait for the function result
4. Repeat until you have enough information to answer

Always think step by step before calling functions."""
                    },
                    *self.conversation_history
                ],
                tools=self.define_tools(),
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                # REASONING is implicit in the model's thought process
                # ACT: Execute tool calls
                for tool_call in message.tool_calls:
                    observation = self.execute_tool(tool_call)
                    
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    
                    # OBSERVE: Add observation
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": observation
                    })
                    
                    print(f"Step {step + 1}: Called {tool_call.function.name}")
                    print(f"Observation: {observation[:100]}...")
            else:
                # Final answer
                return message.content
        
        return "Max steps reached without resolution."

# Usage
agent = ReActAgent(api_key="your-api-key")
result = agent.run("I need to process a refund for order ORD-12345 because it arrived damaged. What's the refund amount?")
print(result)
