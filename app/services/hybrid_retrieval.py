from typing import List, Dict, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx


class HybridRetrieval:
    """Advanced Hybrid retrieval engine with multi-hop reasoning and neighbor boosting"""
    
    def __init__(self, vector_store, graph_store, embedding_generator):
        self.vector_store = vector_store
        self.graph_store = graph_store
        self.embedding_generator = embedding_generator
        self.model = embedding_generator  # For direct encoding access
    
    def normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to [0, 1] range"""
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if min_score == max_score:
            return [0.5] * len(scores)
        
        normalized = [(s - min_score) / (max_score - min_score) for s in scores]
        return normalized
    
    def combine_scores(self, vector_score: float, graph_score: float,
                      vector_weight: float, graph_weight: float) -> float:
        """Combine vector and graph scores"""
        total_weight = vector_weight + graph_weight
        
        if total_weight == 0:
            return 0.0
        
        return (vector_score * vector_weight + graph_score * graph_weight) / total_weight
    
    def hybrid_search(self, query_text: str, alpha: float = 0.6, beta: float = 0.2,
                     gamma: float = 0.2, top_k: int = 5) -> List[Dict]:
        """
        Advanced Hybrid Search with Multi-hop Reasoning and Neighbor Boosting.
        
        Implements the formula:
        Score = (alpha * VectorSim) + (beta * GraphCentrality) + (gamma * NeighborBoost)
        
        This combines:
        1. Vector Similarity: Semantic relevance through embeddings
        2. Graph Centrality: Global importance via PageRank
        3. Neighbor Boost: Local context from neighbors of high-relevance nodes
        
        Args:
            query_text: Text query to search for
            alpha: Weight for Vector Similarity (Semantic relevance) - default 0.6
            beta: Weight for Graph Centrality (Global importance) - default 0.2
            gamma: Weight for Neighbor Proximity (Local context boosting) - default 0.2
            top_k: Number of results to return
        
        Returns:
            List of results with score breakdown showing contribution of each component
        """
        # Validate weights sum to 1.0
        total_weight = alpha + beta + gamma
        if total_weight == 0:
            alpha, beta, gamma = 0.6, 0.2, 0.2
        else:
            # Normalize weights to sum to 1.0
            alpha = alpha / total_weight
            beta = beta / total_weight
            gamma = gamma / total_weight
        
        # 1. Get Vector Scores for ALL nodes
        # We need this to identify "Entry Points" into the graph for neighbor boosting
        try:
            query_vec = self.model.generate_embedding(query_text)
        except:
            query_vec = np.random.randn(384).tolist()  # Fallback to random vector
        
        vec_scores = {}
        
        # Optimization: Loop through all nodes and compute similarity
        # In production, use FAISS for faster approximate nearest neighbor search
        for vector_id, similarity in self.vector_store.search(query_vec, top_k=len(self.graph_store.nodes) or 100):
            metadata = self.vector_store.metadata.get(vector_id, {})
            node_id = metadata.get("node_id")
            if node_id:
                vec_scores[node_id] = float(similarity)
        
        # Fallback: if vector search returns nothing, compute similarities manually
        if not vec_scores and hasattr(self.vector_store, 'vectors'):
            query_vec_array = np.array(query_vec).reshape(1, -1)
            for node_id, vec in self.vector_store.vectors.items():
                vec_array = np.array(vec).reshape(1, -1)
                try:
                    sim = cosine_similarity(query_vec_array, vec_array)[0][0]
                    vec_scores[node_id] = float(sim)
                except:
                    pass
        
        # 2. Identify Top Entry Points (Top K vector matches)
        # These are the "seed" nodes for neighbor boosting
        sorted_vec_nodes = sorted(vec_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top_vector_nodes = {node for node, score in sorted_vec_nodes}
        
        # 3. Calculate Graph Centrality (Global Importance via PageRank)
        try:
            # Build networkx graph from graph_store
            G = nx.DiGraph()
            
            # Add all nodes
            for node_id in self.graph_store.nodes.keys():
                G.add_node(node_id)
            
            # Add all edges with weights
            for node_id, edges in self.graph_store.adjacency.items():
                for edge_data in edges:
                    target_id = edge_data.get("target_id") if isinstance(edge_data, dict) else edge_data
                    weight = edge_data.get("weight", 1.0) if isinstance(edge_data, dict) else 1.0
                    G.add_edge(node_id, target_id, weight=weight)
            
            # Compute PageRank
            centrality = nx.pagerank(G, weight='weight', alpha=0.85)
        except Exception as e:
            # Fallback: simple degree centrality
            centrality = {}
            for node_id in self.graph_store.nodes.keys():
                neighbors = len(self.graph_store.adjacency.get(node_id, []))
                in_degree = len(self.graph_store.reverse_adjacency.get(node_id, []))
                centrality[node_id] = (neighbors + in_degree) / max(len(self.graph_store.nodes), 1)
        
        # 4. Multi-hop Reasoning (Neighbor Boosting)
        # If a node is connected to a Top Vector Match, it gets a score boost.
        # This allows finding "hidden context" that doesn't directly match the query
        # but is related to high-confidence matches.
        neighbor_boost = {n: 0.0 for n in self.graph_store.nodes.keys()}
        
        for main_node in top_vector_nodes:
            if main_node not in self.graph_store.nodes:
                continue
            
            # 1-hop neighbors: direct connections get strong boost
            for edge_data in self.graph_store.adjacency.get(main_node, []):
                neighbor = edge_data.get("target_id") if isinstance(edge_data, dict) else edge_data
                main_score = vec_scores.get(main_node, 0.0)
                # Decay boost by 0.5 so direct vector matches are still preferred
                neighbor_boost[neighbor] = max(
                    neighbor_boost.get(neighbor, 0.0),
                    main_score * 0.5
                )
                
                # Optional: 2-hop neighbors with further decay
                # Uncomment for deeper reasoning (may be slower)
                # for edge_data_2 in self.graph_store.adjacency.get(neighbor, []):
                #     neighbor_2 = edge_data_2.get("target_id") if isinstance(edge_data_2, dict) else edge_data_2
                #     neighbor_boost[neighbor_2] = max(
                #         neighbor_boost.get(neighbor_2, 0.0),
                #         main_score * 0.25
                #     )
        
        # 5. Merge and Rank all nodes using the hybrid formula
        final_scores = []
        all_nodes = set(self.graph_store.nodes.keys())
        
        for node in all_nodes:
            v_score = vec_scores.get(node, 0.0)
            g_score = centrality.get(node, 0.0)
            n_score = neighbor_boost.get(node, 0.0)
            
            # THE HYBRID FORMULA: Weighted combination of three signals
            total_score = (alpha * v_score) + (beta * g_score) + (gamma * n_score)
            
            # Filter out noise (scores below threshold)
            if total_score > 0.01:
                node_data = self.graph_store.get_node(node)
                if node_data:
                    final_scores.append({
                        "node_id": node,
                        "score": float(total_score),
                        "breakdown": {
                            "vector_similarity": round(float(v_score), 4),
                            "graph_centrality": round(float(g_score), 4),
                            "neighbor_boost": round(float(n_score), 4)
                        },
                        "text": node_data.get("text", "")[:100] + "..." if len(node_data.get("text", "")) > 100 else node_data.get("text", ""),
                        "metadata": node_data.get("metadata", {})
                    })
        
        # Sort by total score (descending) and return top_k
        final_scores.sort(key=lambda x: x['score'], reverse=True)
        return final_scores[:top_k]
    
    def multi_hop_reasoning(self, query_text: str, top_k: int = 5,
                           depth: int = 3) -> List[Dict]:
        """
        Multi-hop reasoning query: start from vector search result,
        then explore graph for related nodes
        """
        # Initial vector search
        query_embedding = self.embedding_generator.generate_embedding(query_text)
        vector_results = self.vector_store.search(query_embedding, top_k=1)
        
        if not vector_results:
            return []
        
        # Get starting node from best vector match
        best_vector_id, _ = vector_results[0]
        metadata = self.vector_store.metadata.get(best_vector_id, {})
        start_node_id = metadata.get("node_id")
        
        if not start_node_id:
            return []
        
        # Traverse graph from this node
        traversal = self.graph_store.traverse_bfs(start_node_id, depth=depth)
        
        reasoning_results = []
        
        for node_id, info in traversal.items():
            if node_id == start_node_id:
                relevance = 1.0
            else:
                # Check if this node has semantic similarity to query
                node_data = self.graph_store.get_node(node_id)
                if node_data:
                    node_embedding = self.embedding_generator.generate_embedding(
                        node_data["text"]
                    )
                    relevance = self.vector_store.cosine_similarity(
                        np.array(query_embedding),
                        np.array(node_embedding)
                    )
                else:
                    relevance = 0.0
            
            # Distance-based decay
            distance_decay = 1.0 / (1.0 + info["distance"])
            combined_score = 0.7 * relevance + 0.3 * distance_decay
            
            node_data = self.graph_store.get_node(node_id)
            if node_data:
                reasoning_results.append({
                    "node_id": node_id,
                    "node_text": node_data["text"],
                    "relevance_score": float(relevance),
                    "distance": info["distance"],
                    "path": info["path"],
                    "edge_types": info["edge_types"],
                    "combined_score": float(combined_score),
                    "metadata": node_data.get("metadata", {})
                })
        
        # Sort by combined score
        reasoning_results.sort(key=lambda x: x["combined_score"], reverse=True)
        return reasoning_results[:top_k]
