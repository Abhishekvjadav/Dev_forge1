import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from collections import deque
from pathlib import Path


class GraphStore:
    """Graph storage with nodes, edges, and traversal capabilities"""
    
    def __init__(self, db_path: str = "data/graph.db"):
        self.db_path = db_path
        self.nodes: Dict[str, Dict] = {}  # node_id -> node_data
        self.edges: Dict[str, Dict] = {}  # edge_id -> edge_data
        self.adjacency: Dict[str, List[str]] = {}  # node_id -> [edge_ids]
        self.reverse_adjacency: Dict[str, List[str]] = {}  # node_id -> [edge_ids] (incoming)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for persistence"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                edge_type TEXT,
                weight REAL,
                metadata TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY(source_id) REFERENCES nodes(id),
                FOREIGN KEY(target_id) REFERENCES nodes(id)
            )
        """)
        
        conn.commit()
        conn.close()
        self._load_from_db()
    
    def _load_from_db(self):
        """Load nodes and edges from SQLite into memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load nodes
        cursor.execute("SELECT id, text, metadata, created_at, updated_at FROM nodes")
        rows = cursor.fetchall()
        
        for node_id, text, metadata_json, created_at, updated_at in rows:
            self.nodes[node_id] = {
                "text": text,
                "metadata": json.loads(metadata_json) if metadata_json else {},
                "created_at": created_at,
                "updated_at": updated_at
            }
            self.adjacency[node_id] = []
            self.reverse_adjacency[node_id] = []
        
        # Load edges
        cursor.execute("""
            SELECT id, source_id, target_id, edge_type, weight, metadata 
            FROM edges
        """)
        rows = cursor.fetchall()
        
        for edge_id, source_id, target_id, edge_type, weight, metadata_json in rows:
            self.edges[edge_id] = {
                "source_id": source_id,
                "target_id": target_id,
                "edge_type": edge_type,
                "weight": weight,
                "metadata": json.loads(metadata_json) if metadata_json else {}
            }
            
            if source_id in self.adjacency:
                self.adjacency[source_id].append(edge_id)
            if target_id in self.reverse_adjacency:
                self.reverse_adjacency[target_id].append(edge_id)
        
        conn.close()
    
    def create_node(self, text: str, metadata: Dict = None) -> str:
        """Create a new node"""
        node_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.nodes[node_id] = {
            "text": text,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now
        }
        self.adjacency[node_id] = []
        self.reverse_adjacency[node_id] = []
        
        # Save to DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nodes (id, text, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            node_id,
            text,
            json.dumps(metadata or {}),
            now,
            now
        ))
        conn.commit()
        conn.close()
        
        return node_id
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get node by ID"""
        return self.nodes.get(node_id)
    
    def update_node(self, node_id: str, text: str = None, 
                   metadata: Dict = None) -> bool:
        """Update a node"""
        if node_id not in self.nodes:
            return False
        
        if text is not None:
            self.nodes[node_id]["text"] = text
        
        if metadata is not None:
            self.nodes[node_id]["metadata"] = metadata
        
        now = datetime.now().isoformat()
        self.nodes[node_id]["updated_at"] = now
        
        # Update in DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE nodes SET text = ?, metadata = ?, updated_at = ?
            WHERE id = ?
        """, (
            self.nodes[node_id]["text"],
            json.dumps(self.nodes[node_id]["metadata"]),
            now,
            node_id
        ))
        conn.commit()
        conn.close()
        
        return True
    
    def delete_node(self, node_id: str) -> bool:
        """Delete a node and all associated edges"""
        if node_id not in self.nodes:
            return False
        
        # Delete all edges connected to this node
        edges_to_delete = self.adjacency.get(node_id, []) + self.reverse_adjacency.get(node_id, [])
        
        for edge_id in edges_to_delete:
            self.delete_edge(edge_id)
        
        del self.nodes[node_id]
        del self.adjacency[node_id]
        del self.reverse_adjacency[node_id]
        
        # Delete from DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def create_edge(self, source_id: str, target_id: str, edge_type: str = "related",
                   weight: float = 1.0, metadata: Dict = None) -> str:
        """Create a new edge between two nodes"""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Source or target node does not exist")
        
        edge_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.edges[edge_id] = {
            "source_id": source_id,
            "target_id": target_id,
            "edge_type": edge_type,
            "weight": weight,
            "metadata": metadata or {}
        }
        
        self.adjacency[source_id].append(edge_id)
        self.reverse_adjacency[target_id].append(edge_id)
        
        # Save to DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO edges (id, source_id, target_id, edge_type, weight, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            edge_id,
            source_id,
            target_id,
            edge_type,
            weight,
            json.dumps(metadata or {}),
            now
        ))
        conn.commit()
        conn.close()
        
        return edge_id
    
    def get_edge(self, edge_id: str) -> Optional[Dict]:
        """Get edge by ID"""
        return self.edges.get(edge_id)
    
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge"""
        if edge_id not in self.edges:
            return False
        
        edge = self.edges[edge_id]
        
        if edge["source_id"] in self.adjacency:
            self.adjacency[edge["source_id"]].remove(edge_id)
        
        if edge["target_id"] in self.reverse_adjacency:
            self.reverse_adjacency[edge["target_id"]].remove(edge_id)
        
        del self.edges[edge_id]
        
        # Delete from DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM edges WHERE id = ?", (edge_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def traverse_bfs(self, start_id: str, depth: int = 2,
                    edge_types: List[str] = None) -> Dict[str, Dict]:
        """Breadth-first traversal from start node"""
        if start_id not in self.nodes:
            return {}
        
        visited = {start_id: {"distance": 0, "path": [start_id], "edge_types": []}}
        queue = deque([(start_id, 0, [start_id], [])])
        
        while queue:
            current_id, current_depth, path, edge_types_used = queue.popleft()
            
            if current_depth >= depth:
                continue
            
            # Explore outgoing edges
            for edge_id in self.adjacency.get(current_id, []):
                edge = self.edges[edge_id]
                
                if edge_types and edge["edge_type"] not in edge_types:
                    continue
                
                next_id = edge["target_id"]
                
                if next_id not in visited:
                    new_path = path + [next_id]
                    new_edge_types = edge_types_used + [edge["edge_type"]]
                    visited[next_id] = {
                        "distance": current_depth + 1,
                        "path": new_path,
                        "edge_types": new_edge_types
                    }
                    queue.append((next_id, current_depth + 1, new_path, new_edge_types))
        
        return visited
    
    def traverse_dfs(self, start_id: str, depth: int = 2,
                    edge_types: List[str] = None) -> Dict[str, Dict]:
        """Depth-first traversal from start node"""
        if start_id not in self.nodes:
            return {}
        
        visited = {}
        stack = [(start_id, 0, [start_id], [])]
        
        while stack:
            current_id, current_depth, path, edge_types_used = stack.pop()
            
            if current_id in visited:
                continue
            
            visited[current_id] = {
                "distance": current_depth,
                "path": path,
                "edge_types": edge_types_used
            }
            
            if current_depth >= depth:
                continue
            
            # Explore outgoing edges (in reverse to maintain order)
            edges = self.adjacency.get(current_id, [])[::-1]
            
            for edge_id in edges:
                edge = self.edges[edge_id]
                
                if edge_types and edge["edge_type"] not in edge_types:
                    continue
                
                next_id = edge["target_id"]
                
                if next_id not in visited:
                    new_path = path + [next_id]
                    new_edge_types = edge_types_used + [edge["edge_type"]]
                    stack.append((next_id, current_depth + 1, new_path, new_edge_types))
        
        return visited
    
    def get_neighbors(self, node_id: str, edge_types: List[str] = None) -> List[Tuple[str, str, float]]:
        """Get immediate neighbors of a node"""
        if node_id not in self.nodes:
            return []
        
        neighbors = []
        
        for edge_id in self.adjacency.get(node_id, []):
            edge = self.edges[edge_id]
            
            if edge_types and edge["edge_type"] not in edge_types:
                continue
            
            neighbors.append((
                edge["target_id"],
                edge["edge_type"],
                edge["weight"]
            ))
        
        return neighbors
    
    def get_all_nodes_count(self) -> int:
        """Get total number of nodes"""
        return len(self.nodes)
    
    def get_all_edges_count(self) -> int:
        """Get total number of edges"""
        return len(self.edges)
    
    def clear(self):
        """Clear all nodes and edges"""
        self.nodes.clear()
        self.edges.clear()
        self.adjacency.clear()
        self.reverse_adjacency.clear()
        
        # Clear DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM edges")
        cursor.execute("DELETE FROM nodes")
        conn.commit()
        conn.close()
