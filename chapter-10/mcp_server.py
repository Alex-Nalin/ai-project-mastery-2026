# mcp_server.py
from mcp import Server, Tool, ToolResult
from typing import Dict, Any
import httpx
import sqlite3
import json
from datetime import datetime

class AIToolsServer(Server):
    def __init__(self, name: str = "ai-tools-server"):
        super().__init__(name)
        self.db = sqlite3.connect("tools_data.db")
        self._initialize_database()
        self._register_tools()
    
    def _initialize_database(self):
        """Initialize SQLite database for tool state"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS tool_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT,
                input_params TEXT,
                output TEXT,
                timestamp TEXT,
                success BOOLEAN
            )
        """)
        self.db.commit()
    
    def _register_tools(self):
        """Register all available tools"""
        
        @self.tool(
            name="web_search",
            description="Search the web for current information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results (1-10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        )
        async def web_search(query: str, num_results: int = 5) -> ToolResult:
            """Search the web using a search API"""
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.search.com/v1/search",
                        json={
                            "query": query,
                            "num_results": min(num_results, 10)
                        },
                        headers={"Authorization": "Bearer YOUR_SEARCH_API_KEY"}
                    )
                    results = response.json()
                    
                    # Log the call
                    self._log_tool_call("web_search", {"query": query}, results, True)
                    
                    return ToolResult(
                        success=True,
                        data=results,
                        metadata={
                            "source": "web_search",
                            "timestamp": datetime.now().isoformat(),
                            "result_count": len(results.get("results", []))
                        }
                    )
            except Exception as e:
                self._log_tool_call("web_search", {"query": query}, str(e), False)
                return ToolResult(
                    success=False,
                    error=str(e),
                    metadata={"source": "web_search"}
                )
        
        @self.tool(
            name="execute_code",
            description="Execute Python code in a sandboxed environment",
            parameters={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds",
                        "default": 30
                    }
                },
                "required": ["code"]
            }
        )
        async def execute_code(code: str, timeout: int = 30) -> ToolResult:
            """Execute Python code in a sandboxed environment"""
            try:
                # Use a sandboxed execution environment
                import subprocess
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
                    f.write(code)
                    f.flush()
                    
                    result = subprocess.run(
                        ["python3", "-c", code],
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                    
                    os.unlink(f.name)
                    
                    output = {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "return_code": result.returncode
                    }
                    
                    self._log_tool_call("execute_code", {"code": code[:100]}, output, result.returncode == 0)
                    
                    return ToolResult(
                        success=result.returncode == 0,
                        data=output,
                        metadata={
                            "source": "code_execution",
                            "execution_time": timeout
                        }
                    )
            except subprocess.TimeoutExpired:
                return ToolResult(
                    success=False,
                    error="Code execution timed out",
                    metadata={"source": "code_execution"}
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=str(e),
                    metadata={"source": "code_execution"}
                )
        
        @self.tool(
            name="query_database",
            description="Query the internal SQLite database",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT only)"
                    }
                },
                "required": ["query"]
            }
        )
        async def query_database(query: str) -> ToolResult:
            """Execute read-only SQL queries"""
            try:
                # Ensure read-only
                if not query.strip().upper().startswith("SELECT"):
                    return ToolResult(
                        success=False,
                        error="Only SELECT queries are allowed",
                        metadata={"source": "database"}
                    )
                
                cursor = self.db.execute(query)
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                results = {
                    "columns": columns,
                    "rows": [dict(zip(columns, row)) for row in rows],
                    "row_count": len(rows)
                }
                
                self._log_tool_call("query_database", {"query": query[:100]}, results, True)
                
                return ToolResult(
                    success=True,
                    data=results,
                    metadata={
                        "source": "database",
                        "row_count": len(rows)
                    }
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=str(e),
                    metadata={"source": "database"}
                )
    
    def _log_tool_call(self, tool_name: str, params: Dict, output: Any, success: bool):
        """Log tool call to database for observability"""
        self.db.execute(
            """INSERT INTO tool_calls (tool_name, input_params, output, timestamp, success)
              

VALUES (?, ?, ?, ?, ?)""",
            (tool_name, json.dumps(params), json.dumps(str(output)), datetime.now().isoformat(), success)
        )
        self.db.commit()

# Start the MCP server
if __name__ == "__main__":
    server = AIToolsServer()
    server.run(host="0.0.0.0", port=8080)
