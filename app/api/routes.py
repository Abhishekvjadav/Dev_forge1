from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.models.schemas import (
    NodeCreateRequest, NodeUpdateRequest, NodeResponse,
    EdgeCreateRequest, EdgeResponse,
    VectorSearchRequest, VectorSearchResult,
    GraphTraversalRequest, GraphTraversalResult,
    HybridSearchRequest, HybridSearchResult,
    BulkIngestRequest
)
from datetime import datetime

router = APIRouter()

# Global stores (will be injected)
vector_store = None
graph_store = None
embedding_generator = None
hybrid_retrieval = None


def set_stores(vs, gs, eg, hr):
    global vector_store, graph_store, embedding_generator, hybrid_retrieval
    vector_store = vs
    graph_store = gs
    embedding_generator = eg
    hybrid_retrieval = hr


# ============== NODE CRUD ==============

@router.post("/nodes", response_model=NodeResponse, tags=["Nodes"])
async def create_node(request: NodeCreateRequest):
    """Create a new node with optional embedding"""
    try:
        # Create node in graph store
        node_id = graph_store.create_node(request.text, request.metadata)
        
        # Generate or use provided embedding
        if request.embedding:
            embedding = request.embedding
        else:
            embedding = embedding_generator.generate_embedding(request.text)
        
        # Store embedding in vector store
        vector_store.add_vector(node_id, embedding, {"node_id": node_id})
        
        # Get created node
        node_data = graph_store.get_node(node_id)
        
        return NodeResponse(
            id=node_id,
            text=node_data["text"],
            metadata=node_data["metadata"],
            embedding=embedding,
            created_at=datetime.fromisoformat(node_data["created_at"]),
            updated_at=datetime.fromisoformat(node_data["updated_at"]),
            edges=graph_store.adjacency.get(node_id, [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/nodes/{node_id}", response_model=NodeResponse, tags=["Nodes"])
async def get_node(node_id: str):
    """Get a node by ID"""
    node_data = graph_store.get_node(node_id)
    
    if not node_data:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return NodeResponse(
        id=node_id,
        text=node_data["text"],
        metadata=node_data["metadata"],
        embedding=None,  # Don't return embedding for privacy
        created_at=datetime.fromisoformat(node_data["created_at"]),
        updated_at=datetime.fromisoformat(node_data["updated_at"]),
        edges=graph_store.adjacency.get(node_id, [])
    )


@router.put("/nodes/{node_id}", response_model=NodeResponse, tags=["Nodes"])
async def update_node(node_id: str, request: NodeUpdateRequest):
    """Update a node"""
    if not graph_store.get_node(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    
    try:
        # Update node
        graph_store.update_node(node_id, request.text, request.metadata)
        
        # Regenerate embedding if text was updated
        if request.text:
            new_embedding = embedding_generator.generate_embedding(request.text)
            # Find vector ID for this node and update it
            for vector_id, metadata in vector_store.metadata.items():
                if metadata.get("node_id") == node_id:
                    vector_store.update_vector(vector_id, new_embedding)
                    break
        
        node_data = graph_store.get_node(node_id)
        
        return NodeResponse(
            id=node_id,
            text=node_data["text"],
            metadata=node_data["metadata"],
            embedding=None,
            created_at=datetime.fromisoformat(node_data["created_at"]),
            updated_at=datetime.fromisoformat(node_data["updated_at"]),
            edges=graph_store.adjacency.get(node_id, [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/nodes/{node_id}", tags=["Nodes"])
async def delete_node(node_id: str):
    """Delete a node and all its edges"""
    if not graph_store.get_node(node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    
    try:
        # Delete vector
        for vector_id, metadata in list(vector_store.metadata.items()):
            if metadata.get("node_id") == node_id:
                vector_store.delete_vector(vector_id)
                break
        
        # Delete node (and associated edges)
        graph_store.delete_node(node_id)
        
        return {"status": "success", "message": f"Node {node_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== EDGE CRUD ==============

@router.post("/edges", response_model=EdgeResponse, tags=["Edges"])
async def create_edge(request: EdgeCreateRequest):
    """Create a new edge between two nodes"""
    try:
        edge_id = graph_store.create_edge(
            request.source_id,
            request.target_id,
            request.edge_type,
            request.weight,
            request.metadata
        )
        
        edge_data = graph_store.get_edge(edge_id)
        
        return EdgeResponse(
            id=edge_id,
            source_id=edge_data["source_id"],
            target_id=edge_data["target_id"],
            edge_type=edge_data["edge_type"],
            weight=edge_data["weight"],
            metadata=edge_data["metadata"],
            created_at=datetime.now()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edges/{edge_id}", response_model=EdgeResponse, tags=["Edges"])
async def get_edge(edge_id: str):
    """Get an edge by ID"""
    edge_data = graph_store.get_edge(edge_id)
    
    if not edge_data:
        raise HTTPException(status_code=404, detail="Edge not found")
    
    return EdgeResponse(
        id=edge_id,
        source_id=edge_data["source_id"],
        target_id=edge_data["target_id"],
        edge_type=edge_data["edge_type"],
        weight=edge_data["weight"],
        metadata=edge_data["metadata"],
        created_at=datetime.now()
    )


@router.delete("/edges/{edge_id}", tags=["Edges"])
async def delete_edge(edge_id: str):
    """Delete an edge"""
    if not graph_store.get_edge(edge_id):
        raise HTTPException(status_code=404, detail="Edge not found")
    
    try:
        graph_store.delete_edge(edge_id)
        return {"status": "success", "message": f"Edge {edge_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== VECTOR SEARCH ==============

@router.post("/search/vector", response_model=List[VectorSearchResult], tags=["Search"])
async def vector_search(request: VectorSearchRequest):
    """Search using vector similarity"""
    try:
        query_embedding = embedding_generator.generate_embedding(request.query_text)
        vector_results = vector_store.search(query_embedding, top_k=request.top_k)
        
        results = []
        for vector_id, similarity in vector_results:
            metadata = vector_store.metadata.get(vector_id, {})
            node_id = metadata.get("node_id")
            
            if node_id:
                node_data = graph_store.get_node(node_id)
                if node_data:
                    results.append(VectorSearchResult(
                        node_id=node_id,
                        node_text=node_data["text"],
                        similarity_score=float(similarity),
                        metadata=node_data.get("metadata", {})
                    ))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== GRAPH TRAVERSAL ==============

@router.get("/search/graph", response_model=List[GraphTraversalResult], tags=["Search"])
async def graph_traversal(
    start_id: str = Query(..., description="Starting node ID"),
    depth: int = Query(2, ge=1, le=10, description="Traversal depth"),
    edge_types: Optional[str] = Query(None, description="Comma-separated edge types to filter")
):
    """Traverse graph from a starting node"""
    try:
        if not graph_store.get_node(start_id):
            raise HTTPException(status_code=404, detail="Start node not found")
        
        edge_types_list = None
        if edge_types:
            edge_types_list = [e.strip() for e in edge_types.split(",")]
        
        traversal = graph_store.traverse_bfs(start_id, depth=depth, edge_types=edge_types_list)
        
        results = []
        for node_id, info in traversal.items():
            node_data = graph_store.get_node(node_id)
            if node_data:
                results.append(GraphTraversalResult(
                    node_id=node_id,
                    node_text=node_data["text"],
                    distance=info["distance"],
                    path=info["path"],
                    edge_types=info["edge_types"],
                    metadata=node_data.get("metadata", {})
                ))
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== HYBRID SEARCH ==============

@router.post("/search/hybrid", response_model=List[HybridSearchResult], tags=["Search"])
async def hybrid_search(request: HybridSearchRequest):
    """
    Advanced Hybrid Search with Multi-hop Reasoning.
    
    Combines three signals for improved retrieval:
    - Vector Similarity: Semantic relevance through embeddings
    - Graph Centrality: Global importance via PageRank
    - Neighbor Boost: Local context from neighbors of high-relevance nodes
    
    Returns results with score breakdown showing contribution of each component.
    """
    try:
        results = hybrid_retrieval.hybrid_search(
            query_text=request.query,
            alpha=request.alpha,
            beta=request.beta,
            gamma=request.gamma,
            top_k=request.top_k
        )
        
        return [HybridSearchResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== MULTI-HOP REASONING ==============

@router.post("/search/multihop", response_model=List[HybridSearchResult], tags=["Search"])
async def multi_hop_reasoning(
    query_text: str = Query(..., description="Query text"),
    top_k: int = Query(5, ge=1, le=100, description="Number of results"),
    depth: int = Query(3, ge=1, le=10, description="Traversal depth")
):
    """
    Multi-hop reasoning query.
    
    Starts from the best vector match and explores related nodes in the graph.
    Returns a path through the knowledge graph that leads to contextually relevant nodes.
    """
    try:
        results = hybrid_retrieval.multi_hop_reasoning(
            query_text=query_text,
            top_k=top_k,
            depth=depth
        )
        
        # Convert multi-hop results to HybridSearchResult format
        converted = []
        for r in results:
            converted.append({
                "node_id": r["node_id"],
                "score": r["combined_score"],
                "text": r["node_text"],
                "breakdown": {
                    "vector_similarity": r["relevance_score"],
                    "graph_centrality": 1.0 / (1.0 + r["distance"]) if r["distance"] > 0 else 1.0,
                    "neighbor_boost": 0.0  # Not applicable for multi-hop
                },
                "metadata": r["metadata"]
            })
        
        return [HybridSearchResult(**result) for result in converted]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== BULK OPERATIONS ==============

@router.post("/bulk/ingest", tags=["Bulk"])
async def bulk_ingest(request: BulkIngestRequest):
    """Bulk ingest nodes and edges"""
    try:
        node_mapping = {}
        
        # Create nodes
        for node_req in request.nodes:
            node_id = graph_store.create_node(node_req.text, node_req.metadata)
            
            if node_req.embedding:
                embedding = node_req.embedding
            else:
                embedding = embedding_generator.generate_embedding(node_req.text)
            
            vector_store.add_vector(node_id, embedding, {"node_id": node_id})
            node_mapping[len(node_mapping)] = node_id
        
        # Create edges
        if request.edges:
            for edge_req in request.edges:
                try:
                    graph_store.create_edge(
                        edge_req.source_id,
                        edge_req.target_id,
                        edge_req.edge_type,
                        edge_req.weight,
                        edge_req.metadata
                    )
                except ValueError:
                    pass  # Skip invalid edges
        
        return {
            "status": "success",
            "nodes_created": len(node_mapping),
            "edges_created": len(request.edges) if request.edges else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== SYSTEM INFO ==============

@router.get("/status", tags=["System"])
async def get_status():
    """Get system status and statistics"""
    try:
        return {
            "total_nodes": graph_store.get_all_nodes_count(),
            "total_edges": graph_store.get_all_edges_count(),
            "total_vectors": vector_store.get_all_vectors_count(),
            "vector_dimension": vector_store.embedding_dim,
            "storage_type": "SQLite + In-Memory",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
