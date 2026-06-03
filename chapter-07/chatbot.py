# support_chatbot/chatbot.py
"""Customer support chatbot with learning capabilities."""

import os
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document


class SupportChatbot:
    """Intelligent customer support chatbot."""

    def __init__(
        self,
        pinecone_index: str = "support-knowledge",
        model: str = "gpt-4o",
    ) -> None:
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Initialize vector store
        self.vector_store = PineconeVectorStore(
            index_name=pinecone_index,
            embedding=self.embeddings,
        )

        # Conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        # Setup the chain
        self.chain = self._create_chain()

        # Track new knowledge for learning
        self.new_knowledge: List[Document] = []

    def _create_prompt(self) -> PromptTemplate:
        """Create the prompt template."""
        template = """You are a helpful customer support agent. 
        Use the following context to answer the user's question.
        If you don't know the answer, say so honestly.
        
        Context:
        {context}
        
        Chat History:
        {chat_history}
        
        Question: {question}
        
        Provide a helpful, accurate response. If you learned something 
        new from this interaction that should be added to the knowledge 
        base, indicate it with [NEW_KNOWLEDGE] at the end."""

        return PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"],
        )

    def _create_chain(self):
        """Create the conversational retrieval chain."""
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5},
        )

        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": self._create_prompt()},
            return_source_documents=True,
            verbose=True,
        )

    def chat(self, message: str) -> Dict:
        """Process a chat message and return response."""
        result = self.chain.invoke({"question": message})

        response = {
            "answer": result["answer"],
            "sources": [
                {
                    "content": doc.page_content[:200],
                    "metadata": doc.metadata,
                }
                for doc in result["source_documents"]
            ],
        }

        # Check for new knowledge
        if "[NEW_KNOWLEDGE]" in result["answer"]:
            self._extract_new_knowledge(message, result["answer"])

        return response

    def _extract_new_knowledge(self, question: str, answer: str) -> None:
        """Extract and validate new knowledge from conversations."""
        # Use LLM to extract factual knowledge
        extraction_prompt = f"""
        Extract factual knowledge from this Q&A pair that should 
        be added to the knowledge base.
        
        Question: {question}
        Answer: {answer}
        
        Return the factual knowledge as a concise statement, 
        or 'NONE' if no new factual knowledge is present.
        """

        extraction = self.llm.invoke(extraction_prompt)

        if extraction.content != "NONE":
            doc = Document(
                page_content=extraction.content,
                metadata={
                    "source": "conversation",
                    "timestamp": datetime.now().isoformat(),
                    "question": question,
                    "verified": False,  # Needs human review
                },
            )
            self.new_knowledge.append(doc)

    def commit_learning(self) -> Dict:
        """Add validated new knowledge to the vector store."""
        if self.new_knowledge:
            self.vector_store.add_documents(self.new_knowledge)
            count = len(self.new_knowledge)
            self.new_knowledge = []
            return {"committed": count}
        return {"committed": 0}
