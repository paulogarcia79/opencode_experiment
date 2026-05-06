---
description: Build a queryable knowledge graph from code, docs, papers, or images
---

Build a queryable knowledge graph from the repository.

**Usage:**
- `/graphify <path>` — Full pipeline on specific path
- `/graphify <path> --update` — Incremental update (only changed files)
- `/graphify query "<question>"` — Query an existing graph

**Prerequisite:** Activate the virtual environment first:
```bash
source .venv/bin/activate
```

**Outputs (in graphify-out/):**
- `graph.html` — Interactive visualization
- `GRAPH_REPORT.md` — Audit report with god nodes & surprising connections
- `graph.json` — Queryable graph data

When invoked, load the `graphify` skill and follow its instructions.
