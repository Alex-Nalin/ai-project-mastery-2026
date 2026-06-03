"""
MCP Server for Customer Database
Exposes customer data, order history, and analytics to AI agents.
"""

import sqlite3
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

class CustomerDatabase:
    """Internal database handler."""
    
    def __init__(self, db_path: str = "customers.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with sample data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                tier TEXT DEFAULT 'standard',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                product TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
            
            -- Insert sample data if empty
            INSERT OR IGNORE INTO customers (id, name, email, tier) VALUES
                (1, 'Alice Johnson', 'alice@example.com', 'premium'),
                (2, 'Bob Smith', 'bob@example.com', 'standard'),
                (3, 'Charlie Brown', 'charlie@example.com', 'enterprise');
                
            INSERT OR IGNORE INTO orders (id, customer_id, product, amount, status) VALUES
                (101, 1, 'Laptop Pro', 2499.99, 'shipped'),
                (102, 1, 'Wireless Mouse', 79.99, 'delivered'),
                (103, 2, 'Monitor 4K', 599.99, 'pending'),
                (104, 3, 'Server Rack', 12999.99, 'processing');
        """)
        
        conn.commit()
        conn.close()
    
    def get_customer(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_customer_orders(self, customer_id: int) -> List[Dict]:
        """Get all orders for a customer."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_customers(self, query: str) -> List[Dict]:
        """Search customers by name or email."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM customers WHERE name LIKE ? OR email LIKE ?",
            (f"%{query}%", f"%{query}%")
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_analytics(self) -> Dict:
        """Get database analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(amount) FROM orders")
        total_revenue = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT tier, COUNT(*) as count 
            FROM customers GROUP BY tier
        """)
        tier_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "tier_distribution": tier_distribution
        }

# Initialize database handler
db = CustomerDatabase()

# Create MCP server instance
server = Server("customer-database")

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available resources (data endpoints)."""
    return [
        types.Resource(
            uri="customers://all",
            name="All Customers",
            description="List of all customers in the database",
            mimeType="application/json"
        ),
        types.Resource(
            uri="customers://analytics",
            name="Customer Analytics",
            description="Aggregated analytics about customers and orders",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    if uri == "customers://all":
        customers = db.search_customers("")
        return json.dumps(customers, indent=2)
    elif uri == "customers://analytics":
        analytics = db.get_analytics()
        return json.dumps(analytics, indent=2)
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools (actions the agent can take)."""
    return [
        types.Tool(
            name="get_customer",
            description="Get detailed information about a customer by their ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The customer's unique ID"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        types.Tool(
            name="get_customer_orders",
            description="Get all orders for a specific customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "The customer's unique ID"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        types.Tool(
            name="search_customers",
            description="Search for customers by name or email",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for customer name or email"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_analytics",
            description="Get aggregated analytics about customers and orders",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: Dict[str, Any]
) -> List[types.TextContent]:
    """Execute a tool and return results."""
    if name == "get_customer":
        customer_id = arguments["customer_id"]
        customer = db.get_customer(customer_id)
        if customer:
            return [types.TextContent(
                type="text",
                text=json.dumps(customer, indent=2)
            )]
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": "Customer not found"})
            )]
    
    elif name == "get_customer_orders":
        customer_id = arguments["customer_id"]
        orders = db.get_customer_orders(customer_id)
        return [types.TextContent(
            type="text",
            text=json.dumps(orders, indent=2)
        )]
    
    elif name == "search_customers":
        query = arguments["query"]
        customers = db.search_customers(query)
        return [types.TextContent(
            type="text",
            text=json.dumps(customers, indent=2)
        )]
    
    elif name == "get_analytics":
        analytics = db.get_analytics()
        return [types.TextContent(
            type="text",
            text=json.dumps(analytics, indent=2)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="customer-database",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
