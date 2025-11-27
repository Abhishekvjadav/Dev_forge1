import numpy as np
from typing import List
import os


class EmbeddingGenerator:
    """Generate embeddings for text using sentence-transformers or mocked embeddings"""
    
    def __init__(self, use_mock: bool = False, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.use_mock = use_mock
        
        if not use_mock:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dim = 384
            except Exception as e:
                print(f"Warning: Could not load sentence-transformers model ({e}), falling back to mocked embeddings")
                self.use_mock = True
        
        self.embedding_cache = {}
    
    def generate_mock_embedding(self, text: str) -> List[float]:
        """Generate a deterministic mock embedding based on text hash"""
        # Create a simple hash-based embedding
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.normal(0, 0.1, self.embedding_dim)
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # Check cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        if self.use_mock:
            embedding = self.generate_mock_embedding(text)
        else:
            try:
                embedding = self.model.encode(text).tolist()
            except Exception as e:
                print(f"Warning: Embedding generation failed ({e}), using mock embedding")
                embedding = self.generate_mock_embedding(text)
        
        self.embedding_cache[text] = embedding
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        
        for text in texts:
            embeddings.append(self.generate_embedding(text))
        
        return embeddings
    
    def get_embedding_dim(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dim
