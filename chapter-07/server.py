# mcp_knowledge_server/server.py
"""MCP server for vector database access."""

import os
import json
from typing import Optional, List
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import chromadb
from openai import OpenAI


class KnowledgeMCPServer:
    """MCP server that exposes a vector database to AI agents."""

    def __init__(
        self,
        db_path: str = "./knowledge_db",
        collection_name: str = "company_knowledge",
    ) -> None:
        self.server = Server("knowledge-base")
        self.db_path = db_path
        self.collection_name = collection_name

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=db_path)

        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
        except Exception:
            self.collection = self.chroma_client.create_collection(collection_name)

        # Initialize OpenAI for embeddings and generation
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Register tools
        self._register_tools()

    def _register_tools(self) -> None:
        """Register MCP tools."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="query_knowledge_base",
                    description="Query the company knowledge base. "
                    "Returns relevant documents with scores.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query",
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 5,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="add_to_knowledge_base",
                    description="Add a document to the knowledge base.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Document content",
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Document metadata",
                                "default": {},
                            },
                        },
                        "required": ["content"],
                    },
                ),
                Tool(
                    name="get_knowledge_stats",
                    description="Get statistics about the knowledge base.",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            """Handle tool calls."""
            if name == "query_knowledge_base":
                return await self._handle_query(arguments)
            elif name == "add_to_knowledge_base":
                return await self._handle_add(arguments)
            elif name == "get_knowledge_stats":
                return await self._handle_stats()
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_query(self, arguments: dict) -> List[TextContent]:
        """Handle knowledge base query."""
        query = arguments["query"]
        top_k = arguments.get("top_k", 5)

        # Generate embedding for the query
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=query,
        )
        query_embedding = response.data[0].embedding

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        formatted_results = []
        for i in range(len(results["documents"][0])):
            result = {
                "content": results["documents"][0][i][:500],
                "relevance_score": 1 - results["distances"][0][i],
                "metadata": results["metadatas"][0][i],
            }
            formatted_results.append(result)

        return [
            TextContent(
                type="text",
                text=json.dumps(formatted_results, indent=2),
            )
        ]

    async def _handle_add(self, arguments: dict) -> List[TextContent]:
        """Handle adding document to knowledge base."""
        content = arguments["content"]
        metadata = arguments.get("metadata", {})

        # Generate embedding
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=content,
        )
        embedding = response.data[0].embedding

        # Add to ChromaDB
        doc_id = f"doc_{len(self.collection.get()['ids'])}"
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
        )

        return [
            TextContent(
                type="text",
                text=json.dumps({"status": "success", "document_id": doc_id}),
            )
        ]

    async def _handle_stats(self) -> List[TextContent]:
        """Handle getting knowledge base statistics."""
        collection_info = self.collection.get()

        stats = {
            "total_documents": len(collection_info["ids"]),
            "collection_name": self.collection_name,
            "database_path": self.db_path,
        }

        return [
            TextContent(
                type="text",
                text=json.dumps(stats, indent=2),
            )
        ]

    async def run(self) -> None:
        """Run the MCP server."""
        async with self.server.run(
            initialization_options=InitializationOptions(
                server_name="knowledge-base",
                server_version="1.0.0",
                capabilities=self.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )
        ):
            await self.server.wait_for_shutdown()


def main() -> None:
    """Main entry point."""
    import asyncio

    server = KnowledgeMCPServer(
        db_path=os.getenv("KNOWLEDGE_DB_PATH", "./knowledge_db"),
        collection_name=os.getenv("COLLECTION_NAME", "company_knowledge"),
    )

    asyncio.run(server.run())


if __name__ == "__main__":
    main()
