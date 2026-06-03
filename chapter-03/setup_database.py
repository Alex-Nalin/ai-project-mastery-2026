# setup_database.py
import sqlite3

conn = sqlite3.connect("knowledge_base.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Sample data
documents = [
    ("Quantum Computing Basics", 
     "Quantum computing leverages qubits that can exist in superposition states, enabling parallel computation. Current systems use superconducting qubits, trapped ions, or photonic approaches.",
     "Internal Knowledge Base"),
    ("Drug Discovery Pipeline", 
     "Traditional drug discovery takes 10-15 years and costs $2.6 billion on average. Quantum computing promises to reduce this by simulating molecular interactions at quantum scale.",
     "Industry Report 2025"),
    ("Recent Breakthroughs", 
     "In 2025, IBM demonstrated a 1,121-qubit processor. Google achieved quantum supremacy in a drug discovery use case, simulating a caffeine molecule with 99.8% accuracy.",
     "Tech News Archive"),
]

cursor.executemany(
    "INSERT INTO documents (title, content, source) VALUES (?, ?, ?)",
    documents
)

conn.commit()
conn.close()
print("Database initialized with sample documents.")
