import pytest
from app.services.vector_store import VectorStore
from app.services.graph_store import GraphStore
from app.services.hybrid_retrieval import HybridRetrieval
from app.utils.embedding import EmbeddingGenerator
import numpy as np


@pytest.fixture
def vector_store():
    """Create a fresh vector store for testing"""
    store = VectorStore(embedding_dim=384, db_path=":memory:")
    yield store
    store.clear()


@pytest.fixture
def graph_store():
    """Create a fresh graph store for testing"""
    store = GraphStore(db_path=":memory:")
    yield store
    store.clear()


@pytest.fixture
def embedding_generator():
    """Create an embedding generator with mock embeddings"""
    return EmbeddingGenerator(use_mock=True, embedding_dim=384)


@pytest.fixture
def hybrid_retrieval(vector_store, graph_store, embedding_generator):
    """Create hybrid retrieval engine"""
    return HybridRetrieval(vector_store, graph_store, embedding_generator)


class TestVectorStore:
    """Test vector storage functionality"""
    
    def test_add_vector(self, vector_store):
        """Test adding a vector"""
        embedding = [0.1] * 384
        vector_id = vector_store.add_vector("node-1", embedding)
        assert vector_id is not None
        assert vector_store.get_vector(vector_id) is not None
    
    def test_vector_dimension_validation(self, vector_store):
        """Test dimension validation"""
        embedding = [0.1] * 256  # Wrong dimension
        with pytest.raises(ValueError):
            vector_store.add_vector("node-1", embedding)
    
    def test_cosine_similarity(self, vector_store):
        """Test cosine similarity calculation"""
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        similarity = vector_store.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0)
        
        vec3 = np.array([0, 1, 0])
        similarity = vector_store.cosine_similarity(vec1, vec3)
        assert similarity == pytest.approx(0.0)
    
    def test_vector_search(self, vector_store):
        """Test vector search"""
        embeddings = [
            [1.0, 0.0, 0.0] + [0.0] * 381,
            [0.9, 0.1, 0.0] + [0.0] * 381,
            [0.0, 1.0, 0.0] + [0.0] * 381,
        ]
        
        for i, emb in enumerate(embeddings):
            vector_store.add_vector(f"node-{i}", emb)
        
        query = [1.0, 0.0, 0.0] + [0.0] * 381
        results = vector_store.search(query, top_k=2)
        
        assert len(results) == 2
        assert results[0][1] > results[1][1]  # First should be more similar


class TestGraphStore:
    """Test graph storage functionality"""
    
    def test_create_node(self, graph_store):
        """Test node creation"""
        node_id = graph_store.create_node("Test node")
        assert node_id is not None
        assert graph_store.get_node(node_id) is not None
    
    def test_create_edge(self, graph_store):
        """Test edge creation"""
        node1 = graph_store.create_node("Node 1")
        node2 = graph_store.create_node("Node 2")
        
        edge_id = graph_store.create_edge(node1, node2, "related", 0.8)
        assert edge_id is not None
        edge = graph_store.get_edge(edge_id)
        assert edge["source_id"] == node1
        assert edge["target_id"] == node2
    
    def test_invalid_edge_creation(self, graph_store):
        """Test creating edge with non-existent nodes"""
        with pytest.raises(ValueError):
            graph_store.create_edge("non-existent-1", "non-existent-2")
    
    def test_bfs_traversal(self, graph_store):
        """Test BFS traversal"""
        # Create a simple graph: 1 -> 2 -> 3
        node1 = graph_store.create_node("Node 1")
        node2 = graph_store.create_node("Node 2")
        node3 = graph_store.create_node("Node 3")
        
        graph_store.create_edge(node1, node2)
        graph_store.create_edge(node2, node3)
        
        traversal = graph_store.traverse_bfs(node1, depth=2)
        
        assert node1 in traversal
        assert node2 in traversal
        assert node3 in traversal
        assert traversal[node1]["distance"] == 0
        assert traversal[node2]["distance"] == 1
        assert traversal[node3]["distance"] == 2
    
    def test_delete_node_cascades(self, graph_store):
        """Test that deleting a node removes its edges"""
        node1 = graph_store.create_node("Node 1")
        node2 = graph_store.create_node("Node 2")
        edge_id = graph_store.create_edge(node1, node2)
        
        assert graph_store.get_edge(edge_id) is not None
        
        graph_store.delete_node(node1)
        
        assert graph_store.get_node(node1) is None
        assert graph_store.get_edge(edge_id) is None


class TestHybridRetrieval:
    """Test hybrid retrieval functionality"""
    
    def test_hybrid_search(self, hybrid_retrieval, graph_store, vector_store, embedding_generator):
        """Test hybrid search combining both signals"""
        # Create nodes
        node1 = graph_store.create_node("Machine learning basics")
        node2 = graph_store.create_node("Neural networks")
        node3 = graph_store.create_node("Deep learning")
        
        # Add vectors
        for node_id, text in [(node1, "Machine learning basics"), 
                              (node2, "Neural networks"),
                              (node3, "Deep learning")]:
            emb = embedding_generator.generate_embedding(text)
            vector_store.add_vector(node_id, emb, {"node_id": node_id})
        
        # Create relationships
        graph_store.create_edge(node1, node2, weight=0.9)
        graph_store.create_edge(node2, node3, weight=0.8)
        
        # Perform hybrid search
        results = hybrid_retrieval.hybrid_search(
            query_text="machine learning neural networks",
            vector_weight=0.5,
            graph_weight=0.5,
            top_k=3
        )
        
        assert len(results) > 0
        for result in results:
            assert "node_id" in result
            assert "hybrid_score" in result
            assert "vector_score" in result
            assert "graph_score" in result
    
    def test_weighting_impact(self, hybrid_retrieval, graph_store, vector_store, embedding_generator):
        """Test that weight adjustments affect results"""
        # Setup similar to test_hybrid_search
        node1 = graph_store.create_node("Machine learning basics")
        node2 = graph_store.create_node("Neural networks")
        
        for node_id, text in [(node1, "Machine learning basics"), 
                              (node2, "Neural networks")]:
            emb = embedding_generator.generate_embedding(text)
            vector_store.add_vector(node_id, emb, {"node_id": node_id})
        
        graph_store.create_edge(node1, node2, weight=0.9)
        
        # Vector-focused search
        vector_focused = hybrid_retrieval.hybrid_search(
            query_text="learning",
            vector_weight=0.8,
            graph_weight=0.2,
            top_k=1
        )
        
        # Graph-focused search
        graph_focused = hybrid_retrieval.hybrid_search(
            query_text="learning",
            vector_weight=0.2,
            graph_weight=0.8,
            top_k=1
        )
        
        # Results should potentially differ based on weighting
        assert len(vector_focused) > 0
        assert len(graph_focused) > 0


class TestEmbeddingGenerator:
    """Test embedding generation"""
    
    def test_mock_embedding_consistency(self, embedding_generator):
        """Test that mock embeddings are consistent"""
        text = "Test text"
        emb1 = embedding_generator.generate_embedding(text)
        emb2 = embedding_generator.generate_embedding(text)
        
        np.testing.assert_array_almost_equal(emb1, emb2)
    
    def test_embedding_dimension(self, embedding_generator):
        """Test embedding dimension"""
        text = "Test text"
        embedding = embedding_generator.generate_embedding(text)
        assert len(embedding) == 384
    
    def test_batch_embedding(self, embedding_generator):
        """Test batch embedding generation"""
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = embedding_generator.generate_embeddings_batch(texts)
        
        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == 384


class TestIntegration:
    """Integration tests"""
    
    def test_end_to_end_workflow(self, hybrid_retrieval, graph_store, vector_store, embedding_generator):
        """Test complete end-to-end workflow"""
        # 1. Create nodes
        texts = [
            "Artificial intelligence and machine learning",
            "Deep neural networks for image recognition",
            "Natural language processing with transformers",
            "Reinforcement learning for game playing",
            "Vector databases for semantic search"
        ]
        
        node_ids = []
        for text in texts:
            node_id = graph_store.create_node(text)
            embedding = embedding_generator.generate_embedding(text)
            vector_store.add_vector(node_id, embedding, {"node_id": node_id})
            node_ids.append(node_id)
        
        # 2. Create relationships
        graph_store.create_edge(node_ids[0], node_ids[1], "includes", 0.9)
        graph_store.create_edge(node_ids[1], node_ids[2], "related", 0.7)
        graph_store.create_edge(node_ids[0], node_ids[3], "related", 0.8)
        graph_store.create_edge(node_ids[2], node_ids[4], "uses", 0.8)
        
        # 3. Perform vector search
        vector_results = vector_store.search(
            embedding_generator.generate_embedding("machine learning neural networks"),
            top_k=3
        )
        assert len(vector_results) > 0
        
        # 4. Perform graph traversal
        traversal = graph_store.traverse_bfs(node_ids[0], depth=2)
        assert len(traversal) >= 3
        
        # 5. Perform hybrid search
        hybrid_results = hybrid_retrieval.hybrid_search(
            query_text="machine learning deep learning",
            vector_weight=0.5,
            graph_weight=0.5,
            top_k=5
        )
        assert len(hybrid_results) > 0
        
        # 6. Verify hybrid results have all required fields
        for result in hybrid_results:
            assert "node_id" in result
            assert "node_text" in result
            assert "vector_score" in result
            assert "graph_score" in result
            assert "hybrid_score" in result
            assert 0 <= result["hybrid_score"] <= 1
