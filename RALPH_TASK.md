# CyraSoul Multi-Agent Content Framework

## Test Command (Run This to Check Done)
```bash
cd /Users/canokcuer/cyracontent && uv run python -m pytest tests/ -v --tb=short
```

---

## Success Criteria

### Phase 1: Infrastructure [COMPLETE]
- [x] `uv run python -c "import anthropic; print('OK')"` passes
- [x] `curl -s http://localhost:6333/collections | jq '.result.collections | length'` returns 4
- [x] `git remote -v` shows github.com/canokcuer/cyracontent

### Phase 2: Knowledge Base
**Verification:** `uv run python scripts/verify_knowledge.py` returns all green

- [x] Wellness: `curl -s http://localhost:6333/collections/wellness | jq '.result.points_count'` > 0
- [ ] Products: `curl -s http://localhost:6333/collections/products | jq '.result.points_count'` > 0
  - **BLOCKED:** Need product documents from user (DailyGlow, DreamGlow, MindFuel, Reset Button, TheChill)
- [ ] Brand: `curl -s http://localhost:6333/collections/brand | jq '.result.points_count'` > 0
  - **BLOCKED:** Need brand guidelines document from user
- [ ] Scientific: `curl -s http://localhost:6333/collections/scientific | jq '.result.points_count'` > 0
  - **BLOCKED:** Need scientific references from user

### Phase 3: Agent Pipeline
**Verification:** `uv run python scripts/test_pipeline.py` completes without error

- [x] FENIX: `uv run python -c "from src.agents.fenix import FenixAgent; print('OK')"` passes
- [x] HIPPOCRATES: `uv run python -c "from src.agents.hippocrates import HippocratesAgent; print('OK')"` passes
- [x] NEO: `uv run python -c "from src.agents.neo import NeoAgent; print('OK')"` passes
- [x] CAN: `uv run python -c "from src.agents.can import CANOrchestrator; print('OK')"` passes
- [ ] Pipeline test: `uv run python scripts/test_pipeline.py --dry-run` exits 0
- [ ] Integration test: `uv run pytest tests/test_agents.py -v` all pass

### Phase 4: Output Handlers
**Verification:** `uv run python scripts/test_outputs.py` creates valid files

- [x] Markdown: `uv run python -c "from src.outputs.markdown import MarkdownExporter; print('OK')"` passes
- [x] JSON: `uv run python -c "from src.outputs.json_export import JSONExporter; print('OK')"` passes
- [x] Shopify: `uv run python -c "from src.outputs.shopify import ShopifyPublisher; print('OK')"` passes
- [ ] Export test: `uv run python scripts/test_outputs.py` creates files in output/

### Phase 5: End-to-End Generation
**Verification:** Generated article exists and passes validation

- [ ] Generate: `uv run python main.py generate --topic "Uyku Kalitesi" --type blog` exits 0
- [ ] Output exists: `ls output/articles/*.md | head -1` returns a file
- [ ] Word count: Generated article has 1500-2500 words
- [ ] SEO check: Article has H1, 3+ H2s, meta description
- [ ] Turkish check: No English words in main content (except brand names)

---

## Blocked Items (Need User Input)

| Item | What's Needed | Where to Put |
|------|---------------|--------------|
| Product docs | Info for DailyGlow, DreamGlow, MindFuel, Reset Button, TheChill | `knowledge_base/products/` |
| Brand guidelines | CyraSoul tone, voice, style guide | `knowledge_base/brand/` |
| Scientific refs | Research papers, studies to cite | `knowledge_base/scientific/` |
| Shopify creds | Store URL + access token | `.env` file |

---

## Current Focus
**Waiting for user to provide knowledge base documents.**

Once documents are provided:
1. Index them into Qdrant
2. Create verification scripts
3. Test full pipeline
4. Generate sample article

---

## Quick Reference

```bash
# Check Qdrant status
curl -s http://localhost:6333/collections | jq '.result.collections[].name'

# Index a document
uv run python -c "
from src.knowledge.loader import KnowledgeLoader
loader = KnowledgeLoader()
loader.load_and_index('knowledge_base/products/dailyglow.md', 'products')
"

# Test RAG retrieval
uv run python -c "
from src.rag.retriever import RAGRetriever
r = RAGRetriever()
print(r.retrieve('uyku', 'wellness'))
"

# Generate content
uv run python main.py generate --topic 'Uyku Kalitesi' --type blog
```

---

## Definition of Done

**This task is COMPLETE when:**
1. All `[ ]` above are `[x]`
2. `uv run pytest tests/ -v` passes with 0 failures
3. A sample Turkish article exists in `output/articles/`
4. The article passes SEO validation (H1, H2s, meta)
