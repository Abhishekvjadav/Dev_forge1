# 📁 Project Directory Structure

```
vector_graph_db/
│
├── 🚀 STARTUP SCRIPTS
│   ├── run_full_stack.py          ⭐ Run both backend + frontend
│   ├── run_backend.py             📡 Backend API only (port 8000)
│   ├── run_frontend.py            🎨 Frontend only (port 8001)
│   └── run_advanced_demo.py       🎬 Demo with sample data
│
├── 📚 DOCUMENTATION
│   ├── RUN_INSTRUCTIONS.md        ⭐ START HERE - How to run
│   ├── README.md                  📖 Project overview
│   ├── GETTING_STARTED.md         🚀 Quick start guide
│   ├── HYBRID_SEARCH_GUIDE.md     🧠 Algorithm explanation
│   ├── API_DOCUMENTATION.md       📡 API endpoints reference
│   ├── EVALUATION_CHECKLIST.md    ✅ Demo prep checklist
│   ├── UPGRADE_SUMMARY.md         🔄 What was upgraded
│   ├── README_DOCUMENTATION_INDEX.md  🗂️ All docs index
│   └── .gitignore                 Git configuration
│
├── 💻 BACKEND (FastAPI)
│   └── app/
│       ├── main.py                FastAPI application
│       ├── __init__.py
│       │
│       ├── api/
│       │   ├── routes.py          ⭐ All endpoints defined here
│       │   └── __init__.py
│       │
│       ├── models/
│       │   ├── schemas.py         🔹 Pydantic request/response models
│       │   └── __init__.py
│       │
│       ├── services/
│       │   ├── vector_store.py    🔹 Embedding storage & similarity
│       │   ├── graph_store.py     🔹 Knowledge graph storage
│       │   ├── hybrid_retrieval.py ⭐ MAIN: 3-component hybrid search
│       │   └── __init__.py
│       │
│       ├── utils/
│       │   ├── embedding.py       🔹 Embedding generation (SentenceTransformer)
│       │   └── __init__.py
│       │
│       └── static/
│           └── index.html         ⭐ FRONTEND UI (cyberpunk design)
│
├── 🧪 TESTS
│   ├── test_core.py               Unit tests
│   └── __init__.py
│
└── 📦 CONFIGURATION
    └── requirements.txt           Python dependencies

```

## 🎯 Key Directories Explained

### `app/` - Backend Application
- **services/hybrid_retrieval.py** - Core hybrid search engine with 3-component scoring
- **api/routes.py** - All REST API endpoints
- **models/schemas.py** - Request/response data models
- **static/index.html** - Frontend UI (served from here)

### `app/static/` - Frontend Application
- **index.html** - Complete UI with:
  - Dark mode cyberpunk aesthetic
  - Weight sliders (α, β, γ)
  - Results with score breakdown visualization
  - Knowledge graph visualization

## 🚀 Quick Start

```bash
# Run everything with one command
python run_full_stack.py

# OR run separately:
# Terminal 1:
python run_backend.py

# Terminal 2:
python run_frontend.py
```

## 📊 File Summary

| Type | Count | Purpose |
|------|-------|---------|
| 🐍 Python Scripts | 5 | Backend API + startup scripts |
| 📝 Markdown Docs | 8 | Guides, references, checklists |
| 🎨 Frontend | 1 | index.html (500+ lines) |
| 🧪 Tests | 1 | Unit tests for core functionality |
| 📦 Config | 1 | requirements.txt |

## ✨ What's Inside

### Backend Architecture
```
Request → Routes → Hybrid Retrieval Engine
              ├─ Vector Search (embeddings)
              ├─ Graph Centrality (PageRank)
              ├─ Neighbor Boosting (1-hop expansion)
              └─ Score Merge & Rank
              ↓
         Response with Breakdown
```

### Frontend Features
- 🔍 Search box with live query
- ⚙️ Three weight sliders (α, β, γ)
- 📊 Results with visual score breakdown
- 📈 Knowledge graph visualization (Vis.js)
- 🌙 Dark mode cyberpunk aesthetic

## 🗂️ File Sizes

| File | Size | Purpose |
|------|------|---------|
| index.html | 15 KB | Complete UI |
| hybrid_retrieval.py | 8 KB | Core algorithm |
| requirements.txt | 0.5 KB | Dependencies |
| All markdown docs | ~50 KB | Comprehensive guides |

---

**Ready to run? Start with: `python run_full_stack.py`** 🚀
