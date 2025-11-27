# 🚀 How to Run Hybrid Search System

## Quick Start (Recommended)

### Option 1: Full Stack (Backend + Frontend Together)

```bash
python run_full_stack.py
```

This starts both servers automatically:
- **Backend API:** http://localhost:8000 (with docs at /docs)
- **Frontend UI:** http://localhost:8001

---

## Separate Frontend & Backend

### Option 2a: Backend Only

```bash
python run_backend.py
```

Then open: http://localhost:8000/index.html

The backend serves both the API and frontend files.

---

### Option 2b: Backend + Frontend on Separate Ports

**Terminal 1 - Start Backend:**
```bash
python run_backend.py
```

**Terminal 2 - Start Frontend (Port 8001):**
```bash
python run_frontend.py
```

Then open: http://localhost:8001

---

## Installation First Time

If you haven't installed dependencies yet:

```bash
pip install -r requirements.txt
```

---

## Architecture

```
Nexus Hybrid Search
├── Backend (FastAPI + Python)
│   ├── Vector Store (embeddings)
│   ├── Graph Store (knowledge graph)
│   └── Hybrid Retrieval Engine
│
└── Frontend (HTML/CSS/JS)
    ├── Search Interface
    ├── Hybrid Weight Controls
    └── Knowledge Graph Visualization
```

---

## Available Scripts

| Script | Purpose | Port |
|--------|---------|------|
| `run_full_stack.py` | Start both together | 8000 + 8001 |
| `run_backend.py` | Backend API only | 8000 |
| `run_frontend.py` | Frontend only (connects to backend) | 8001 |
| `run_advanced_demo.py` | Demo script with sample queries | - |

---

## Testing the System

### 1. Check Backend Health

```bash
curl http://localhost:8000/status
```

Expected response:
```json
{
    "total_nodes": 0,
    "total_edges": 0,
    "vector_dimension": 384,
    "storage_type": "in-memory",
    "version": "1.0.0"
}
```

### 2. Test Hybrid Search

```bash
curl -X POST "http://localhost:8000/search/hybrid" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "knowledge graph",
    "alpha": 0.6,
    "beta": 0.2,
    "gamma": 0.2,
    "top_k": 5
  }'
```

### 3. View API Documentation

Open: http://localhost:8000/docs

---

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F
```

### Frontend Can't Connect to Backend

Make sure:
1. Backend is running on port 8000
2. CORS is enabled (it is by default)
3. Check browser console for errors (F12)

### Dependencies Missing

```bash
pip install --upgrade -r requirements.txt
```

---

## Demo with Sample Data

Run the advanced demo to see the system in action:

```bash
python run_advanced_demo.py
```

This creates sample Marvel-themed data and runs demo queries.

---

## Environment Variables

Optional configuration:

```bash
# Use mock embeddings (faster, no GPU)
export USE_MOCK_EMBEDDINGS=true

# Then run:
python run_backend.py
```

---

## Next Steps

1. ✅ Start the system with `python run_full_stack.py`
2. 🔍 Open http://localhost:8001 in your browser
3. 📝 Type a query (e.g., "knowledge graph")
4. ⚙️ Adjust the weight sliders to see hybrid scoring in action
5. 📊 Click results to highlight them in the graph visualization

**Enjoy! 🚀**
