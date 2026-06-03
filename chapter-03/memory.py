# langgraph_agent/memory.py
import sqlite3
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict, Any, Optional

class EpisodicMemory:
    """Stores and retrieves past agent experiences."""
    
    def __init__(self, db_path: str = "episodic_memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize FAISS index for similarity search
        self.dimension = 384  # MiniLM embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_to_record = {}
        
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                session_id TEXT,
                action TEXT,
                outcome TEXT,
                success_score REAL,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def store_episode(self, user_id: str, session_id: str, action: str, 
                     outcome: str, success_score: float, context: str):
        """Store an episode with embedding for similarity search."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO episodes (user_id, session_id, action, outcome, 
                                 success_score, context)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, session_id, action, outcome, success_score, context))
        
        episode_id = cursor.lastrowid
        self.conn.commit()
        
        # Add to FAISS index
        embedding = self.encoder.encode(context)
        self.index.add(np.array([embedding]).astype('float32'))
        self.id_to_record[episode_id] = {
            'action': action,
            'outcome': outcome,
            'success_score': success_score,
            'context': context
        }
        
        return episode_id
    
    def retrieve_similar_episodes(self, query: str, k: int = 3) -> List[Dict]:
        """Find past episodes similar to the current situation."""
        query_embedding = self.encoder.encode(query)
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), k
        )
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx in self.id_to_record:
                record = self.id_to_record[idx].copy()
                record['similarity'] = 1.0 / (1.0 + distance)
                results.append(record)
        
        return results
    
    def get_user_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent episodes for a specific user."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT action, outcome, success_score, context, timestamp
            FROM episodes
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        return [
            {
                'action': row[0],
                'outcome': row[1],
                'success_score': row[2],
                'context': row[3],
                'timestamp': row[4]
            }
            for row in cursor.fetchall()
        ]

class LongTermMemory:
    """Persistent knowledge store using vector database."""
    
    def __init__(self, db_path: str = "long_term_memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                category TEXT,
                importance REAL DEFAULT 0.5,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def store(self, key: str, value: str, category: str = "general", 
              importance: float = 0.5, source: str = "agent"):
        """Store a piece of knowledge."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge (key, value, category, importance, source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                importance = MAX(knowledge.importance, excluded.importance),
                updated_at = CURRENT_TIMESTAMP
        """, (key, value, category, importance, source))
        self.conn.commit()
    
    def retrieve(self, key: str) -> Optional[str]:
        """Retrieve knowledge by exact key."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM knowledge WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def search_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Retrieve all knowledge in a category."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT key, value, importance, source, updated_at
            FROM knowledge
            WHERE category = ?
            ORDER BY importance DESC
            LIMIT ?
        """, (category, limit))
        
        return [
            {
                'key': row[0],
                'value': row[1],
                'importance': row[2],
                'source': row[3],
                'updated_at': row[4]
            }
            for row in cursor.fetchall()
        ]
