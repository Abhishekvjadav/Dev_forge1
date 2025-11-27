#!/usr/bin/env python3
"""
Advanced Demo Script for Vector + Graph Database
Showcases Multi-hop Reasoning and Neighbor Boosting
"""

import requests
import json
import time
from typing import List, Dict


API_URL = "http://localhost:8000"


def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def print_result(result: Dict, index: int):
    """Pretty print a single result"""
    print(f"#{index + 1}. Node ID: {result['node_id']}")
    print(f"   Score: {result['score']:.4f}")
    print(f"   Text: {result['text'][:100]}...")
    print()


def demo_create_sample_data():
    """Demo: Create a sample knowledge graph"""
    print_header("BUILDING SAMPLE KNOWLEDGE GRAPH")
    
    # Create nodes
    nodes_data = [
        {"text": "Vector databases store embeddings for semantic search", "metadata": {"type": "vector_db"}},
        {"text": "Embeddings are numerical representations of text meaning", "metadata": {"type": "concept"}},
        {"text": "Semantic similarity measures how closely related two texts are", "metadata": {"type": "concept"}},
        {"text": "Knowledge graphs organize information as connected nodes", "metadata": {"type": "graph_db"}},
        {"text": "Graph databases excel at relationship traversal and reasoning", "metadata": {"type": "graph_db"}},
        {"text": "PageRank identifies important nodes in networks", "metadata": {"type": "algorithm"}},
        {"text": "RAG combines retrieval with generation for better LLM responses", "metadata": {"type": "ai_technique"}},
        {"text": "Cosine similarity measures distance between embedding vectors", "metadata": {"type": "metric"}},
        {"text": "Hybrid search combines vector and graph approaches", "metadata": {"type": "technique"}},
        {"text": "Neighbor boosting finds context through graph connections", "metadata": {"type": "technique"}}
    ]
    
    node_ids = []
    
    for i, data in enumerate(nodes_data):
        response = requests.post(f"{API_URL}/nodes", json=data)
        if response.status_code == 200:
            result = response.json()
            node_ids.append(result['id'])
            print(f"✓ Created node {i+1}: {result['id']}")
        else:
            print(f"✗ Error: {response.text}")
            return []
    
    print(f"\nCreated {len(node_ids)} nodes. Creating relationships...\n")
    
    # Create edges to form a knowledge graph
    edges = [
        # Vector databases node connects to:
        (0, 1, "uses", 0.9),         # Vector DB uses embeddings
        (0, 2, "enables", 0.85),     # Vector DB enables semantic similarity
        (0, 7, "uses_metric", 0.8),  # Vector DB uses cosine similarity
        
        # Embeddings node connects to:
        (1, 2, "enables", 0.8),      # Embeddings enable similarity
        (1, 7, "measured_by", 0.75), # Embeddings measured by cosine similarity
        
        # Graph databases node connects to:
        (3, 4, "is_a", 0.95),        # Graph is a type of database
        (3, 5, "uses", 0.8),         # Graph uses PageRank
        (3, 6, "supports", 0.7),     # Graph supports RAG
        
        # Graph algorithms:
        (4, 5, "uses", 0.85),        # Graph DB uses PageRank
        (5, 6, "improves", 0.7),     # PageRank improves ranking
        
        # Hybrid approach:
        (8, 0, "combines", 0.8),     # Hybrid uses vector DB
        (8, 3, "combines", 0.8),     # Hybrid uses knowledge graph
        (8, 9, "uses", 0.9),         # Hybrid uses neighbor boosting
        (9, 2, "leverages", 0.75),   # Neighbor boosting leverages similarity
    ]
    
    for src, tgt, etype, weight in edges:
        edge_data = {
            "source_id": node_ids[src],
            "target_id": node_ids[tgt],
            "edge_type": etype,
            "weight": weight
        }
        response = requests.post(f"{API_URL}/edges", json=edge_data)
        if response.status_code == 200:
            print(f"✓ Created edge: {node_ids[src][:8]}... → {node_ids[tgt][:8]}... ({etype})")
        else:
            print(f"✗ Error creating edge: {response.text}")
    
    return node_ids


def demo_hybrid_search_comparison():
    """Demo: Compare three search modes"""
    print_header("COMPARING THREE SEARCH MODES")
    
    query = "How do embeddings improve search?"
    print(f"Query: '{query}'\n")
    
    modes = [
        ("VECTOR-ONLY (Semantic baseline)", {"query": query, "alpha": 1.0, "beta": 0.0, "gamma": 0.0, "top_k": 3}),
        ("GRAPH-ONLY (Structure baseline)", {"query": query, "alpha": 0.0, "beta": 1.0, "gamma": 0.0, "top_k": 3}),
        ("HYBRID BALANCED (Advanced)", {"query": query, "alpha": 0.6, "beta": 0.2, "gamma": 0.2, "top_k": 5}),
    ]
    
    for mode_name, params in modes:
        print(f"\n{'─'*80}")
        print(f"Mode: {mode_name}")
        print(f"{'─'*80}\n")
        
        response = requests.post(f"{API_URL}/search/hybrid", json=params)
        
        if response.status_code == 200:
            results = response.json()
            for idx, result in enumerate(results):
                print(f"#{idx + 1}. {result['node_id']}")
                print(f"    Total Score: {result['score']:.4f}")
                
                if 'breakdown' in result:
                    bd = result['breakdown']
                    print(f"    ├─ Vector Similarity:  {bd.get('vector_similarity', 0):.4f}")
                    print(f"    ├─ Graph Centrality:   {bd.get('graph_centrality', 0):.4f}")
                    print(f"    └─ Neighbor Boost:     {bd.get('neighbor_boost', 0):.4f}")
                
                print(f"    Text: {result['text']}\n")
        else:
            print(f"✗ Error: {response.text}\n")


def demo_neighbor_boosting():
    """Demo: Show how neighbor boosting works"""
    print_header("NEIGHBOR BOOSTING IN ACTION")
    
    print("""
The key advantage of Hybrid Search is NEIGHBOR BOOSTING:

When you query "What is RAG?":
  1. Vector search finds nodes mentioning "retrieval" and "generation"
  2. Graph search checks connectivity
  3. Neighbor boosting applies a score multiplier to neighbors of high-relevance nodes

Example:
  - "RAG" node matches query (vector score: 0.92)
  - "LLMs" is a neighbor of "RAG" (connected by edge)
  - Even if "LLMs" doesn't mention "retrieval", it gets boosted because:
    * LLMs are conceptually related to RAG
    * The graph shows the connection
    * Neighbor boost = parent_score × 0.5 = 0.92 × 0.5 = 0.46

This mimics human reasoning: "If RAG is important and connects to LLMs, 
LLMs are probably important for understanding RAG."
    """)
    
    query = "What are the key components?"
    print(f"\nDemonstrating with query: '{query}'\n")
    
    response = requests.post(
        f"{API_URL}/search/hybrid",
        json={"query": query, "alpha": 0.6, "beta": 0.2, "gamma": 0.2, "top_k": 5}
    )
    
    if response.status_code == 200:
        results = response.json()
        print("Results showing NEIGHBOR BOOST contribution:\n")
        
        for idx, result in enumerate(results):
            bd = result.get('breakdown', {})
            neighbor_boost = bd.get('neighbor_boost', 0)
            
            print(f"#{idx + 1}. {result['node_id']}")
            
            # Show which component contributed most
            components = [
                ('Vector', bd.get('vector_similarity', 0)),
                ('Graph', bd.get('graph_centrality', 0)),
                ('Neighbor', neighbor_boost)
            ]
            
            if neighbor_boost > 0.05:
                print(f"    ✓ NEIGHBOR BOOST APPLIED: {neighbor_boost:.4f}")
                print(f"      → This node was found because it's connected to a relevant match!")
            
            print(f"    Score breakdown: Vector={bd.get('vector_similarity', 0):.3f}, "
                  f"Graph={bd.get('graph_centrality', 0):.3f}, "
                  f"Neighbor={neighbor_boost:.3f}")
            print(f"    Total: {result['score']:.4f}\n")


def demo_multihop_reasoning():
    """Demo: Multi-hop reasoning"""
    print_header("MULTI-HOP REASONING (Graph Traversal)")
    
    query = "How do embeddings and graphs work together?"
    
    print(f"Query: '{query}'\n")
    print("Starting from best vector match, exploring graph up to 3 hops away...\n")
    
    response = requests.post(
        f"{API_URL}/search/multihop",
        params={"query_text": query, "top_k": 5, "depth": 3}
    )
    
    if response.status_code == 200:
        results = response.json()
        print("Multi-hop reasoning results:\n")
        
        for idx, result in enumerate(results):
            print(f"#{idx + 1}. {result['node_id']}")
            print(f"    Score: {result['score']:.4f}")
            print(f"    Text: {result['text']}\n")
    else:
        print(f"Note: Multi-hop demo requires data. Error: {response.text}")


def demo_system_stats():
    """Demo: System statistics"""
    print_header("SYSTEM STATUS")
    
    response = requests.get(f"{API_URL}/status")
    
    if response.status_code == 200:
        status = response.json()
        print(f"Total Nodes:         {status.get('total_nodes', 0)}")
        print(f"Total Edges:         {status.get('total_edges', 0)}")
        print(f"Vector Dimension:    {status.get('vector_dimension', 384)}")
        print(f"Storage Type:        {status.get('storage_type', 'In-Memory')}")
        print(f"Version:             {status.get('version', '1.0.0')}")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("  Vector + Graph Hybrid Database")
    print("  Advanced Hybrid Search with Multi-hop Reasoning & Neighbor Boosting")
    print("="*80)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/status")
        if response.status_code != 200:
            print("\n✗ API is not running.")
            print("   Start the API with: python -m app.main")
            return
    except Exception as e:
        print(f"\n✗ Cannot connect to API at {API_URL}")
        print(f"   Error: {e}")
        print("   Start the API with: python -m app.main")
        return
    
    print("\n✓ API is running!\n")
    
    # Run demos
    demo_system_stats()
    time.sleep(1)
    
    print("\n" + "="*80)
    print("  Building sample knowledge graph for demonstration...")
    print("="*80)
    node_ids = demo_create_sample_data()
    
    if not node_ids:
        print("✗ Failed to create sample data. Exiting.")
        return
    
    time.sleep(2)
    
    demo_hybrid_search_comparison()
    time.sleep(2)
    
    demo_neighbor_boosting()
    time.sleep(2)
    
    demo_multihop_reasoning()
    
    print("\n" + "="*80)
    print("  Demo Complete!")
    print("="*80)
    print("\n  📊 Open Web UI: http://localhost:8000/index.html")
    print("  📚 Read Guide: ./HYBRID_SEARCH_GUIDE.md")
    print("  🔧 API Docs: http://localhost:8000/docs")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
