from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class NodeCreateRequest(BaseModel):
    """Request model for creating a node"""
    text: str = Field(..., description="Text content of the node")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Optional pre-computed embedding")


class NodeUpdateRequest(BaseModel):
    """Request model for updating a node"""
    text: Optional[str] = Field(default=None, description="Updated text content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Updated metadata")


class NodeResponse(BaseModel):
    """Response model for a node"""
    id: str
    text: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]]
    created_at: datetime
    updated_at: datetime
    edges: List[str] = Field(default_factory=list, description="List of connected edge IDs")


class EdgeCreateRequest(BaseModel):
    """Request model for creating an edge"""
    source_id: str = Field(..., description="Source node ID")
    target_id: str = Field(..., description="Target node ID")
    edge_type: str = Field(default="related", description="Type of relationship")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Edge weight (0-1)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class EdgeResponse(BaseModel):
    """Response model for an edge"""
    id: str
    source_id: str
    target_id: str
    edge_type: str
    weight: float
    metadata: Dict[str, Any]
    created_at: datetime


class VectorSearchRequest(BaseModel):
    """Request model for vector search"""
    query_text: str = Field(..., description="Query text to search for")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of top results to return")


class VectorSearchResult(BaseModel):
    """Result model for vector search"""
    node_id: str
    node_text: str
    similarity_score: float
    metadata: Dict[str, Any]


class GraphTraversalRequest(BaseModel):
    """Request model for graph traversal"""
    start_id: str = Field(..., description="Starting node ID")
    depth: int = Field(default=2, ge=1, le=10, description="Traversal depth")
    edge_types: Optional[List[str]] = Field(default=None, description="Filter by edge types")


class GraphTraversalResult(BaseModel):
    """Result model for graph traversal"""
    node_id: str
    node_text: str
    distance: int
    path: List[str]
    edge_types: List[str]
    metadata: Dict[str, Any]


class HybridSearchRequest(BaseModel):
    """Request model for advanced hybrid search with multi-hop reasoning"""
    query: str = Field(..., description="Query text to search for")
    alpha: float = Field(default=0.6, ge=0.0, le=1.0, description="Weight for vector similarity (semantic relevance)")
    beta: float = Field(default=0.2, ge=0.0, le=1.0, description="Weight for graph centrality (global importance)")
    gamma: float = Field(default=0.2, ge=0.0, le=1.0, description="Weight for neighbor proximity (local context boosting)")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of top results to return")


class HybridSearchResult(BaseModel):
    """Result model for advanced hybrid search with breakdown"""
    node_id: str
    score: float
    text: str
    breakdown: Dict[str, float]  # Contains vector_similarity, graph_centrality, neighbor_boost
    metadata: Dict[str, Any]


class BulkIngestRequest(BaseModel):
    """Request model for bulk ingestion"""
    nodes: List[NodeCreateRequest]
    edges: Optional[List[EdgeCreateRequest]] = Field(default=None)


class StatusResponse(BaseModel):
    """Response model for system status"""
    total_nodes: int
    total_edges: int
    vector_dimension: int
    storage_type: str
    version: str
