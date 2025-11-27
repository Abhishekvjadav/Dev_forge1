# API Documentation - Vector + Graph Database

## Overview

This document provides comprehensive API documentation for the Vector + Graph Native Database system.

**Base URL**: `http://localhost:8000`

**API Version**: 1.0.0

## Table of Contents
1. [Authentication](#authentication)
2. [Request/Response Format](#requestresponse-format)
3. [Node Endpoints](#node-endpoints)
4. [Edge Endpoints](#edge-endpoints)
5. [Search Endpoints](#search-endpoints)
6. [Bulk Operations](#bulk-operations)
7. [System Endpoints](#system-endpoints)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

---

## Authentication

Currently, no authentication is required. All endpoints are public.

Future versions may include:
- API key authentication
- Rate limiting
- User-specific data isolation

---

## Request/Response Format

### Content-Type
All requests should use `Content-Type: application/json`

### Response Format
All responses follow this pattern:

**Success Response (2xx)**
```json
{
  "data": {...},
  "status": "success"
}
```

**Error Response (4xx/5xx)**
```json
{
  "detail": "Error message",
  "status": "error"
}
```

### Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `top_k` | integer | Number of results to return (1-100) |
| `depth` | integer | Graph traversal depth (1-10) |
| `vector_weight` | float | Vector similarity weight (0.0-1.0) |
| `graph_weight` | float | Graph closeness weight (0.0-1.0) |

---

## Node Endpoints

### Create Node
Creates a new node with optional embedding and metadata.

**Endpoint**: `POST /nodes`

**Request Body**:
```json
{
  "text": "Node content or description",
  "metadata": {
    "category": "ML",
    "source": "wiki",
    "tags": ["ai", "learning"]
  },
  "embedding": [optional array of floats]
}
```

**Response** (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Node content or description",
  "metadata": {
    "category": "ML",
    "source": "wiki",
    "tags": ["ai", "learning"]
  },
  "embedding": [0.123, -0.456, ...],
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "edges": []
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Machine Learning is a subset of artificial intelligence",
    "metadata": {"category": "ML", "complexity": "beginner"}
  }'
```

---

### Get Node
Retrieves a node by ID.

**Endpoint**: `GET /nodes/{node_id}`

**Response** (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Node content",
  "metadata": {...},
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "edges": ["edge-id-1", "edge-id-2"]
}
```

**Errors**:
- `404`: Node not found

**Example**:
```bash
curl http://localhost:8000/nodes/550e8400-e29b-41d4-a716-446655440000
```

---

### Update Node
Updates a node's text and/or metadata.

**Endpoint**: `PUT /nodes/{node_id}`

**Request Body**:
```json
{
  "text": "Updated text",
  "metadata": {"updated": true, "version": 2}
}
```

**Response** (200):
Updated node object

**Errors**:
- `404`: Node not found
- `400`: Invalid request

**Example**:
```bash
curl -X PUT http://localhost:8000/nodes/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Updated content",
    "metadata": {"updated_at": "2024-01-15"}
  }'
```

---

### Delete Node
Deletes a node and all its associated edges.

**Endpoint**: `DELETE /nodes/{node_id}`

**Response** (200):
```json
{
  "status": "success",
  "message": "Node xxx deleted"
}
```

**Errors**:
- `404`: Node not found

**Example**:
```bash
curl -X DELETE http://localhost:8000/nodes/550e8400-e29b-41d4-a716-446655440000
```

---

## Edge Endpoints

### Create Edge
Creates a relationship between two nodes.

**Endpoint**: `POST /edges`

**Request Body**:
```json
{
  "source_id": "node-id-1",
  "target_id": "node-id-2",
  "edge_type": "related",
  "weight": 0.8,
  "metadata": {
    "strength": "strong",
    "date_added": "2024-01-15"
  }
}
```

**Response** (201):
```json
{
  "id": "edge-id-123",
  "source_id": "node-id-1",
  "target_id": "node-id-2",
  "edge_type": "related",
  "weight": 0.8,
  "metadata": {...},
  "created_at": "2024-01-15T10:30:00"
}
```

**Common Edge Types**:
- `related`: General relationship
- `extends`: Extends or builds upon
- `cites`: References or cites
- `similar`: Similar topic or content
- `contradicts`: Contradicts or opposes
- `refines`: Refines or improves upon

**Errors**:
- `400`: Source or target node doesn't exist
- `400`: Invalid weight (outside 0-1 range)

**Example**:
```bash
curl -X POST http://localhost:8000/edges \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "node-1",
    "target_id": "node-2",
    "edge_type": "cites",
    "weight": 0.9
  }'
```

---

### Get Edge
Retrieves an edge by ID.

**Endpoint**: `GET /edges/{edge_id}`

**Response** (200):
Edge object

**Errors**:
- `404`: Edge not found

---

### Delete Edge
Deletes an edge.

**Endpoint**: `DELETE /edges/{edge_id}`

**Response** (200):
```json
{
  "status": "success",
  "message": "Edge xxx deleted"
}
```

---

## Search Endpoints

### Vector Search
Finds nodes based on semantic similarity to query text.

**Endpoint**: `POST /search/vector`

**Request Body**:
```json
{
  "query_text": "What is machine learning?",
  "top_k": 10
}
```

**Response** (200):
```json
[
  {
    "node_id": "node-1",
    "node_text": "Machine learning is a branch of AI...",
    "similarity_score": 0.92,
    "metadata": {"category": "ML"}
  },
  {
    "node_id": "node-2",
    "node_text": "Deep learning uses neural networks...",
    "similarity_score": 0.87,
    "metadata": {"category": "DL"}
  }
]
```

**Parameters**:
- `query_text` (string, required): Text to search for
- `top_k` (integer, optional): Number of results (default: 10, max: 100)

**How It Works**:
1. Generates embedding for query text
2. Computes cosine similarity with all stored embeddings
3. Returns top_k most similar nodes
4. Scores indicate semantic relevance (0-1)

**Example**:
```bash
curl -X POST http://localhost:8000/search/vector \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "optimization algorithms",
    "top_k": 5
  }'
```

---

### Graph Traversal
Explores nodes reachable from a starting point.

**Endpoint**: `GET /search/graph`

**Query Parameters**:
- `start_id` (string, required): Starting node ID
- `depth` (integer, optional): How far to traverse (default: 2, max: 10)
- `edge_types` (string, optional): Comma-separated edge types to follow

**Response** (200):
```json
[
  {
    "node_id": "node-1",
    "node_text": "Starting node",
    "distance": 0,
    "path": ["node-1"],
    "edge_types": [],
    "metadata": {}
  },
  {
    "node_id": "node-2",
    "node_text": "Adjacent node",
    "distance": 1,
    "path": ["node-1", "node-2"],
    "edge_types": ["cites"],
    "metadata": {}
  }
]
```

**Algorithm**: Breadth-first search (BFS)

**Performance**: O(V + E) where V = nodes, E = edges

**Example**:
```bash
# Get all nodes within 2 hops
curl "http://localhost:8000/search/graph?start_id=node-1&depth=2"

# Only follow specific relationship types
curl "http://localhost:8000/search/graph?start_id=node-1&depth=3&edge_types=cites,extends"
```

---

### Hybrid Search ⭐ (Core Feature)
Combines vector similarity with graph relationships for superior relevance.

**Endpoint**: `POST /search/hybrid`

**Request Body**:
```json
{
  "query_text": "neural network optimization",
  "vector_weight": 0.5,
  "graph_weight": 0.5,
  "top_k": 10,
  "depth": 2,
  "start_id": null
}
```

**Response** (200):
```json
[
  {
    "node_id": "node-1",
    "node_text": "Gradient descent optimization for neural networks",
    "vector_score": 0.92,
    "graph_score": 0.85,
    "hybrid_score": 0.885,
    "distance": 1,
    "similarity_score": 0.92,
    "metadata": {}
  }
]
```

**Parameters**:
- `query_text` (string, required): Text to search for
- `vector_weight` (float, optional): Weight for semantic similarity (0-1, default: 0.5)
- `graph_weight` (float, optional): Weight for relationship closeness (0-1, default: 0.5)
- `top_k` (integer, optional): Number of results (default: 10)
- `depth` (integer, optional): Graph traversal depth (default: 2)
- `start_id` (string, optional): Starting node for graph traversal

**Scoring Formula**:
```
hybrid_score = (vector_score × vector_weight + graph_score × graph_weight) / (vector_weight + graph_weight)
```

**Weighting Strategies**:
- **Semantic-focused** (0.7/0.3): Find conceptually related content
- **Relationship-focused** (0.3/0.7): Find closely connected content
- **Balanced** (0.5/0.5): Find relevant AND connected content (recommended)

**Example**:
```bash
# Balanced search
curl -X POST http://localhost:8000/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "deep learning architectures",
    "vector_weight": 0.5,
    "graph_weight": 0.5,
    "top_k": 10
  }'

# Semantic-focused search
curl -X POST http://localhost:8000/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "distributed training",
    "vector_weight": 0.8,
    "graph_weight": 0.2,
    "top_k": 5
  }'
```

---

### Multi-hop Reasoning
Advanced query that starts from semantic match then explores relationships.

**Endpoint**: `POST /search/multihop`

**Query Parameters**:
- `query_text` (string, required): Initial search query
- `top_k` (integer, optional): Number of results (default: 5)
- `depth` (integer, optional): Traversal depth (default: 3)

**Response** (200):
```json
[
  {
    "node_id": "node-1",
    "node_text": "Query matching result",
    "relevance_score": 0.95,
    "distance": 0,
    "path": ["node-1"],
    "edge_types": [],
    "combined_score": 0.95
  },
  {
    "node_id": "node-5",
    "node_text": "Related concept 2 hops away",
    "relevance_score": 0.72,
    "distance": 2,
    "path": ["node-1", "node-3", "node-5"],
    "edge_types": ["extends", "cites"],
    "combined_score": 0.82
  }
]
```

**Algorithm**:
1. Vector search: Find single best match
2. Graph traversal: Explore from that node
3. Scoring: Combine relevance + proximity
4. Rank and return results

**Example**:
```bash
curl -X POST "http://localhost:8000/search/multihop?query_text=federated%20learning&top_k=10&depth=3"
```

---

## Bulk Operations

### Bulk Ingest
Create multiple nodes and edges in one request.

**Endpoint**: `POST /bulk/ingest`

**Request Body**:
```json
{
  "nodes": [
    {
      "text": "Node 1 text",
      "metadata": {"id": 1}
    },
    {
      "text": "Node 2 text",
      "metadata": {"id": 2}
    }
  ],
  "edges": [
    {
      "source_id": "node-id-1",
      "target_id": "node-id-2",
      "edge_type": "related",
      "weight": 0.8
    }
  ]
}
```

**Response** (200):
```json
{
  "status": "success",
  "nodes_created": 2,
  "edges_created": 1
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/bulk/ingest \
  -H "Content-Type: application/json" \
  -d @bulk_data.json
```

---

## System Endpoints

### Get System Status
Returns database statistics and configuration.

**Endpoint**: `GET /status`

**Response** (200):
```json
{
  "total_nodes": 156,
  "total_edges": 342,
  "total_vectors": 156,
  "vector_dimension": 384,
  "storage_type": "SQLite + In-Memory",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/status
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error description"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful search or retrieval |
| 201 | Created | Node or edge created |
| 400 | Bad Request | Invalid JSON or parameters |
| 404 | Not Found | Node/edge doesn't exist |
| 500 | Server Error | Internal processing error |

### Common Errors

**404 - Not Found**
```json
{"detail": "Node not found"}
```

**400 - Bad Request**
```json
{"detail": "Source or target node does not exist"}
```

**500 - Server Error**
```json
{"detail": "Invalid embedding dimension. Expected 384, got 256"}
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Create first node
NODE1=$(curl -s -X POST http://localhost:8000/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Deep learning uses artificial neural networks",
    "metadata": {"category": "DL"}
  }' | jq -r '.id')

# 2. Create second node
NODE2=$(curl -s -X POST http://localhost:8000/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Neural networks are inspired by biological neurons",
    "metadata": {"category": "NN"}
  }' | jq -r '.id')

# 3. Create edge between them
curl -X POST http://localhost:8000/edges \
  -H "Content-Type: application/json" \
  -d "{
    \"source_id\": \"$NODE1\",
    \"target_id\": \"$NODE2\",
    \"edge_type\": \"uses\",
    \"weight\": 0.9
  }"

# 4. Vector search
curl -X POST http://localhost:8000/search/vector \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "neural networks and deep learning",
    "top_k": 5
  }'

# 5. Graph traversal
curl "http://localhost:8000/search/graph?start_id=$NODE1&depth=2"

# 6. Hybrid search
curl -X POST http://localhost:8000/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "deep learning neural networks",
    "vector_weight": 0.6,
    "graph_weight": 0.4,
    "top_k": 10
  }'
```

### Research Paper Graph Example

```bash
# Create research papers as nodes
curl -X POST http://localhost:8000/bulk/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [
      {"text": "Attention is All You Need (Transformer)", "metadata": {"year": 2017}},
      {"text": "BERT: Pre-training of Deep Bidirectional", "metadata": {"year": 2018}},
      {"text": "GPT-3: Language Models are Few-Shot", "metadata": {"year": 2020}}
    ],
    "edges": [
      {"source_id": "node-1", "target_id": "node-2", "edge_type": "cites", "weight": 0.9},
      {"source_id": "node-2", "target_id": "node-3", "edge_type": "cites", "weight": 0.8}
    ]
  }'

# Find papers related to transformers
curl -X POST http://localhost:8000/search/hybrid \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "transformer attention mechanisms",
    "top_k": 5
  }'
```

---

## Pagination and Filtering

All search endpoints support:
- `top_k`: Limit results
- `depth`: Limit graph traversal
- `edge_types`: Filter relationship types

Future versions will add:
- Offset-based pagination
- Date range filtering
- Metadata filtering

---

## Rate Limiting

Currently unrestricted. Future versions will implement:
- 1000 requests per minute per IP
- 100 concurrent connections
- Query timeout: 30 seconds

---

## Changelog

### v1.0.0 (Current)
- Initial release
- All core CRUD endpoints
- Vector search with cosine similarity
- Graph traversal (BFS/DFS)
- Hybrid retrieval combining both
- Multi-hop reasoning
- SQLite persistence
- FastAPI with OpenAPI documentation

---

**For more information, see README.md**
