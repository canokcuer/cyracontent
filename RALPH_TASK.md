# CyraSoul Multi-Agent Content Framework

## Task Overview
Build and operate a multi-agent RAG system for generating Turkish wellness content for cyrasoul.com.

## Test Commands
```bash
# Verify Qdrant is running
curl -s http://localhost:6333/collections | jq

# Test RAG retrieval
cd /Users/canokcuer/cyracontent && uv run python -c "
from src.rag.retriever import RAGRetriever
r = RAGRetriever()
results = r.retrieve('uyku kalitesi', collection='wellness')
print(f'Found {len(results)} results')
"

# Run unit tests
cd /Users/canokcuer/cyracontent && uv run pytest tests/ -v
```

---

## Success Criteria

### Phase 1: Infrastructure Setup
- [x] Project structure created
- [x] Dependencies installed (claude-agent-sdk, qdrant-client, voyageai)
- [x] Qdrant running locally (Docker)
- [x] Collections created (wellness, products, scientific, brand)
- [x] Voyage AI embeddings working
- [x] Git repository initialized and pushed

### Phase 2: Knowledge Base
- [x] quickguide.md indexed into wellness collection (14 chunks)
- [ ] Product information indexed (DailyGlow, DreamGlow, MindFuel, Reset Button, TheChill)
- [ ] Brand guidelines indexed
- [ ] Scientific references indexed

### Phase 3: Agent Implementation
- [x] FENIX agent skeleton created (content writer)
- [x] HIPPOCRATES agent skeleton created (scientific reviewer)
- [x] NEO agent skeleton created (SEO optimizer)
- [x] CAN orchestrator skeleton created
- [ ] Agent prompts refined with knowledge context
- [ ] Agent handoff logic tested
- [ ] Full pipeline tested end-to-end

### Phase 4: Output Handlers
- [x] Markdown exporter created
- [x] JSON exporter created
- [x] Shopify integration created
- [ ] Output format validation tested
- [ ] Shopify API connection verified

### Phase 5: End-to-End Test
- [ ] Generate sample article: "Uyku Kalitesini Artirmanin 10 Yolu"
- [ ] Verify Turkish content quality
- [ ] Check scientific accuracy (HIPPOCRATES review)
- [ ] Validate SEO optimization (NEO review)
- [ ] Export to all formats (md, json, shopify)

---

## Current Focus
Phase 2: Adding more knowledge base documents (products, brand guidelines)

## Files to Reference
- `.ralph/guardrails.md` - Learned constraints and signs
- `.ralph/progress.md` - Detailed progress log
- `state/guardrails.md` - Content generation rules (Turkish)
- `config/agents.yaml` - Agent configurations

## Agent Architecture
```
CAN (Orchestrator)
  ├── FENIX (Writer) → Uses RAG for wellness knowledge
  ├── HIPPOCRATES (Reviewer) → Validates scientific claims
  └── NEO (SEO) → Optimizes for Turkish search
```

## Key Constraints
1. All content must be in Turkish
2. Never make unverified health claims
3. Max 2-3 product mentions per article
4. Follow CyraSoul brand voice (bilimsel ama samimi)
