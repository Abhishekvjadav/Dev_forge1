from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from app.services.vector_store import VectorStore
from app.services.graph_store import GraphStore
from app.services.hybrid_retrieval import HybridRetrieval
from app.utils.embedding import EmbeddingGenerator
from app.api import routes
import os
from pathlib import Path


def create_app():
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Vector + Graph Native Database",
        description="Hybrid retrieval system combining vector embeddings with graph relationships",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize stores
    use_mock_embeddings = os.getenv("USE_MOCK_EMBEDDINGS", "false").lower() == "true"
    
    vector_store = VectorStore(embedding_dim=384, db_path="data/vectors.db")
    graph_store = GraphStore(db_path="data/graph.db")
    embedding_generator = EmbeddingGenerator(use_mock=use_mock_embeddings)
    hybrid_retrieval = HybridRetrieval(vector_store, graph_store, embedding_generator)
    
    # Set stores in routes
    routes.set_stores(vector_store, graph_store, embedding_generator, hybrid_retrieval)
    
    # Include router FIRST (so API routes take priority)
    app.include_router(routes.router)
    
    # Mount static files at /static (not root) to avoid conflicts
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        try:
            app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        except Exception as e:
            print(f"Warning: Could not mount static files: {e}")
    
    @app.on_event("startup")
    async def startup_event():
        """Handle startup"""
        print("Vector + Graph Database initialized")
        print(f"Using mock embeddings: {use_mock_embeddings}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle shutdown"""
        print("Shutting down Vector + Graph Database")
    
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "Vector + Graph Native Database API",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
