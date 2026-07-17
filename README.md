# AEO Product Ops System

A multi-agent system that audits, tests, and prioritizes what to fix for AI-answer-engine visibility — built to explore how product management works when "search" means being cited by ChatGPT/Perplexity/AI Overviews instead of ranking on a results page.

## The problem

A growing share of search queries now get answered directly by AI, with no click-through to a website. Companies have spent 20 years optimizing for traditional ranking factors, but there's no simple, repeatable way to measure whether a page is actually structured to be *cited* by an AI answer engine, or to turn that signal into a prioritized action plan the way SEO tools have long done for search ranking.

## What this does

Simulates a small cross-functional product team as five agents:

1. **Technical SEO Agent** — fetches the target page for real and checks schema markup (JSON-LD), title/meta tags, and heading structure
2. **AEO Signal Agent** — tests buyer queries to see if the target page gets cited by AI search, vs. up to 3 competitors
3. **Content Strategy Agent** — proposes specific content fixes grounded in the Technical SEO + AEO Signal findings
4. **Competitive Intel Agent** — synthesizes a citation-share benchmark against competitors from the AEO Signal data
5. **PM Synthesizer Agent** — turns all four agents' (often conflicting) findings into one RICE-scored, prioritized roadmap, a one-page PRD for the top item, and a stakeholder summary

The system closes the loop: re-run an audit against the same target/competitors/queries and it links the new run back to the original (`parent_run_id`), computes a citation-rate before/after comparison, and marks roadmap items as resolved once the underlying finding is fixed.

## How this works (and what's mocked)

**All 5 agents — Technical SEO, AEO Signal, Content Strategy, Competitive Intel, and PM Synthesizer — currently run on deterministic mocked logic, not real Anthropic API calls.** This is by design: real Claude API access requires billing to be configured, which isn't set up for this build, so each agent file is clearly marked `# MOCKED — replace with real Anthropic API call once billing is set up`.

What's real vs. simulated, agent by agent:

- **Technical SEO** does make a real HTTP fetch of the target page — the schema/JSON-LD, title/meta, and heading data it reports is genuinely scraped from the live page. Only the interpretation and scoring on top of that real data is mocked.
- **AEO Signal** and **Competitive Intel** are fully simulated: citation results are generated deterministically (a hash of `domain + query`, so the same input always produces the same output) rather than by actually asking an AI search engine whether it cites the page. They do not reflect real AI search behavior.
- **Content Strategy** and **PM Synthesizer** are template-based logic over the other agents' (real or mocked) outputs, not LLM-generated text.

Adding a real `ANTHROPIC_API_KEY` plus wiring the Anthropic `web_search` tool into the AEO Signal and Competitive Intel agents (per Doc 02 of `docs/project-docs.md`) is what would turn this from an architecture demo into a live measurement tool — the orchestration, database, and frontend around it are already built to support that swap without other changes.

## Architecture

```mermaid
flowchart TD
    User[User] -->|fills form| Frontend["Next.js Frontend<br/>(Vercel)"]
    Frontend -->|REST/JSON| Backend["FastAPI Backend<br/>(Railway/Render)"]
    Backend --> DB[(SQLite)]

    subgraph Orchestrator["Pipeline (app/orchestrator.py)"]
        direction LR
        A1[Technical SEO Agent] --> A3[Content Strategy Agent]
        A2[AEO Signal Agent] --> A3
        A2 --> A4[Competitive Intel Agent]
        A1 --> A5[PM Synthesizer Agent]
        A2 --> A5
        A3 --> A5
        A4 --> A5
    end

    Backend --> Orchestrator
    A1 -->|real HTTP fetch| TargetPage[Target page]
    Orchestrator --> DB
```

- **Frontend** (`/frontend`): Next.js 14 (App Router) + TypeScript + Tailwind. Home page (run an audit) · History (past runs, re-run for comparison) · Report (roadmap, PRD, stakeholder summary, before/after view).
- **Backend** (`/backend`): FastAPI, orchestrating the 5 agents in dependency order per run, persisting each agent's result and the resulting RICE roadmap to SQLite.
- **Database**: SQLite (`runs`, `agent_results`, `roadmap_items` — see `docs/project-docs.md` Doc 05 for the full schema).

## Local setup

**Backend:**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # fill in ANTHROPIC_API_KEY / PAGESPEED_API_KEY when ready — not required for the mocked agents to run
uvicorn app.main:app --reload --port 8000
```

**Frontend** (separate terminal):
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Then open `http://localhost:3000`.

## Deployment

- **Frontend → Vercel**: import the repo, set the project's root directory to `frontend`, and set `NEXT_PUBLIC_API_BASE_URL` to your deployed backend's URL.
- **Backend → Railway or Render**: root directory `backend`, build command `pip install -r requirements.txt`, start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (a `Procfile` with this is already included). Set `FRONTEND_ORIGINS` to your deployed Vercel URL so CORS allows it.
- SQLite on most free-tier PaaS disks is **ephemeral** — data can be wiped on redeploy/restart. Fine for a portfolio demo; swap `DATABASE_URL` for a managed Postgres if you need real persistence.

## Before/After Result

<!-- TODO: fill in with a real before/after run — screenshot or describe the
     citation-rate change from an actual fix you shipped between two runs. -->

## Stack

Python (FastAPI) + Next.js, calling the Anthropic API directly — no agent framework dependency.
