import numpy as np
from typing import List, Dict, Tuple, Optional
import sqlite3
import json
from datetime import datetime
import uuid
from pathlib import Path


class VectorStore:
    """Vector storage and similarity search implementation"""
    
    def __init__(self, embedding_dim: int = 384, db_path: str = "data/vectors.db"):
        self.embedding_dim = embedding_dim
        self.db_path = db_path
        self.vectors: Dict[str, np.ndarray] = {}  # In-memory cache
        self.metadata: Dict[str, Dict] = {}  # Metadata for each vector
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistence"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                node_id TEXT NOT NULL UNIQUE,
                embedding BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        self._load_from_db()
    
    def _load_from_db(self):
        """Load vectors from SQLite into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, embedding, metadata FROM vectors")
        rows = cursor.fetchall()
        
        for row in rows:
            vector_id, embedding_blob, metadata_json = row
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            self.vectors[vector_id] = embedding
            if metadata_json:
                self.metadata[vector_id] = json.loads(metadata_json)
        
        conn.close()
    
    def _save_to_db(self, vector_id: str, node_id: str, embedding: np.ndarray, 
                    metadata: Dict = None, created_at: datetime = None, 
                    updated_at: datetime = None):
        """Save vector to SQLite"""
        if created_at is None:
            created_at = datetime.now()
        if updated_at is None:
            updated_at = datetime.now()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO vectors (id, node_id, embedding, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            vector_id,
            node_id,
            embedding.astype(np.float32).tobytes(),
            json.dumps(metadata or {}),
            created_at.isoformat(),
            updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def add_vector(self, node_id: str, embedding: List[float], 
                   metadata: Dict = None) -> str:
        """Add a vector to storage"""
        if embedding is None:
            raise ValueError("Embedding cannot be None")
        
        embedding_array = np.array(embedding, dtype=np.float32)
        
        if len(embedding_array) != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch. Expected {self.embedding_dim}, got {len(embedding_array)}"
            )
        
        vector_id = str(uuid.uuid4())
        self.vectors[vector_id] = embedding_array
        self.metadata[vector_id] = {
            "node_id": node_id,
            **(metadata or {})
        }
        
        self._save_to_db(vector_id, node_id, embedding_array, 
                        {"node_id": node_id, **(metadata or {})})
        
        return vector_id
    
    def update_vector(self, vector_id: str, embedding: List[float],
                     metadata: Dict = None) -> bool:
        """Update an existing vector"""
        if vector_id not in self.vectors:
            return False
        
        embedding_array = np.array(embedding, dtype=np.float32)
        
        if len(embedding_array) != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension mismatch. Expected {self.embedding_dim}, got {len(embedding_array)}"
            )
        
        self.vectors[vector_id] = embedding_array
        if metadata is not None:
            node_id = self.metadata[vector_id].get("node_id")
            self.metadata[vector_id] = {"node_id": node_id, **metadata}
        
        # Update in DB
        node_id = self.metadata[vector_id].get("node_id")
        self._save_to_db(vector_id, node_id, embedding_array, 
                        self.metadata[vector_id], updated_at=datetime.now())
        
        return True
    
    def get_vector(self, vector_id: str) -> Optional[np.ndarray]:
        """Get a vector by ID"""
        return self.vectors.get(vector_id)
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector"""
        if vector_id not in self.vectors:
            return False
        
        del self.vectors[vector_id]
        if vector_id in self.metadata:
            del self.metadata[vector_id]
        
        # Delete from DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vectors WHERE id = ?", (vector_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar vectors"""
        if not self.vectors:
            return []
        
        query_array = np.array(query_embedding, dtype=np.float32)
        
        if len(query_array) != self.embedding_dim:
            raise ValueError(
                f"Query embedding dimension mismatch. Expected {self.embedding_dim}, got {len(query_array)}"
            )
        
        similarities = []
        
        for vector_id, vector in self.vectors.items():
            similarity = self.cosine_similarity(query_array, vector)
            similarities.append((vector_id, similarity))
        
        # Sort by similarity descending and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_all_vectors_count(self) -> int:
        """Get total number of vectors"""
        return len(self.vectors)
    
    def clear(self):
        """Clear all vectors"""
        self.vectors.clear()
        self.metadata.clear()
        
        # Clear DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vectors")
        conn.commit()
        conn.close()
