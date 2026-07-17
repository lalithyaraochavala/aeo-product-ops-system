# AEO Product Ops System — Project Documents
*Six pre-build documents, filled out for Claude Code as the source of truth.*

---

## 01 — PRD (Product Requirements Document)

| Field | Detail |
|---|---|
| **App Name** | AEO Product Ops System |
| **Tagline** | A virtual product team that audits, tests, and prioritizes what to fix for AI-answer-engine visibility. |
| **Problem** | Companies have spent 20 years optimizing for ranked search results, but a growing share of queries now get answered directly by AI (Google AI Overviews, ChatGPT, Perplexity, Claude) with no click-through. There's no simple, repeatable way to measure whether a page is actually structured to be *cited* by these engines, or to turn that signal into a prioritized action plan the way SEO tools have long done for ranking. |
| **Target User** | A product manager or content lead at a B2B software/marketplace company (e.g. a G2/Capterra-type platform) who owns organic growth and needs to decide, every sprint, what to fix first across schema markup, content structure, and technical SEO — without three separate specialist teams' worth of manual audits. |
| **Core Value Proposition** | Instead of a single audit tool, this simulates the whole cross-functional team (Technical SEO, AEO Signal testing, Content Strategy, Competitive Intel) and — critically — a PM Synthesizer agent that turns their conflicting findings into one prioritized, engineering-ready roadmap. It also *closes the loop*: re-tests citation behavior after a fix ships, so recommendations are backed by before/after data, not theory. |
| **Core Features (Must Have)** | 1. Technical SEO Agent — crawls a URL, checks schema markup (JSON-LD), title/meta tags, basic Core Web Vitals<br>2. AEO Signal Agent — runs real buyer queries via web search / LLM-with-search and logs whether the target domain is cited, and against whom<br>3. Content Strategy Agent — proposes specific content edits based on SEO + AEO findings<br>4. Competitive Intel Agent — runs the same citation tests against 2–3 competitor domains<br>5. PM Synthesizer Agent — produces a RICE-scored prioritized roadmap + a one-page PRD for the top item + a plain-English stakeholder summary<br>6. Report history — every run is saved so before/after comparisons are possible<br>7. Simple dashboard to trigger a run, watch agent progress, and read the final report |
| **Nice to Have** | - Scheduled re-runs (weekly citation re-check on saved pages)<br>- Trend chart of citation rate over time per page<br>- Export roadmap/PRD as PDF or Markdown<br>- Slack notification when a report finishes |
| **Out of Scope (v1)** | - No multi-user accounts or auth — single-user personal tool<br>- No automatic implementation of fixes (recommendations only, human implements)<br>- No support for JS-heavy pages requiring headless browser rendering (static HTML fetch only)<br>- No paid SEO API integrations (Ahrefs/Semrush) — v1 uses free/low-cost sources only |
| **User Stories** | - As a PM, I want to enter a URL and get a full AEO/SEO audit so that I don't have to manually check schema, content structure, and citation behavior myself.<br>- As a PM, I want the conflicting findings from different "specialists" synthesized into one prioritized list so that I know what to bring to engineering first.<br>- As a PM, I want to see whether my page is cited by AI search vs. my competitors' so that I can benchmark, not guess.<br>- As a PM, I want to re-run the audit after a fix ships so that I can prove the recommendation worked with real before/after data. |
| **Success Metrics** | - End-to-end run (URL in → roadmap out) completes in under 3 minutes<br>- At least one real before/after experiment completed and documented with an actual citation-rate change<br>- Roadmap output is clean enough to screenshot directly into a portfolio/interview deck without editing |

---

## 02 — TRD (Technical Requirements Document)

> **Assumption flagged:** I picked a stack that's fast to build solo, free-tier friendly, and demo-able — swap anything below before building if you have a preference.

| Field | Detail |
|---|---|
| **Frontend** | Next.js 14 (App Router) + TypeScript + Tailwind CSS — chosen so the final report/dashboard looks polished for a portfolio screenshot/demo, not just terminal output |
| **Backend** | Python (FastAPI) — hosts the 5-agent orchestration logic and exposes it as an API the frontend calls |
| **Database** | SQLite (via `sqlite3` or `SQLModel`) — no external DB needed for a single-user demo tool; stores run history for before/after comparisons |
| **Auth** | None (v1) — single-user local/personal tool. *(Flag: if you want this publicly demoable, add a simple API-key gate later — not full auth.)* |
| **Hosting** | Frontend: Vercel (free tier). Backend: Railway or Render (free/hobby tier) — or run both locally for interview demos, which is fine for a portfolio project |
| **Core AI Provider** | Anthropic Claude API (`claude-sonnet-4-6`) — used directly, no LangGraph/CrewAI dependency, per your "just Claude" decision |
| **Third-Party APIs/Tools** | - Anthropic Messages API (agent calls)<br>- Anthropic web_search tool (for AEO Signal + Competitive Intel agents)<br>- Google PageSpeed Insights API (free) — Core Web Vitals<br>- `requests` + `BeautifulSoup`/`extruct` (Python) — HTML fetch + schema/JSON-LD parsing |
| **Key Libraries** | Backend: `fastapi`, `uvicorn`, `sqlmodel`, `requests`, `beautifulsoup4`, `extruct`, `anthropic`.<br>Frontend: `react-query` or `swr`, `recharts` (for citation trend charts), `lucide-react` |
| **Folder Structure** | ```/backend/app/agents/ (one file per agent)/backend/app/orchestrator.py/backend/app/api.py/backend/app/db.py/backend/app/tools/ (schema_checker.py, pagespeed.py, web_search_wrapper.py)/frontend/app/ (Next.js routes)/frontend/components/``` |
| **Environment Variables** | `ANTHROPIC_API_KEY`, `PAGESPEED_API_KEY`, `DATABASE_URL` (defaults to local sqlite file if unset) |
| **Constraints** | - Must run entirely on free-tier services for the demo<br>- Full pipeline run must complete in under ~3 minutes to stay usable in a live interview demo<br>- Keep each agent's system prompt + logic in its own file so the "5 separate roles" structure is visually obvious in the repo (important for the portfolio story) |

---

## 03 — App Flow

| Field | Detail |
|---|---|
| **Pages** | `/` (home — enter URL + competitor URLs, start run) · `/run/[id]` (live progress — shows each agent completing in sequence) · `/report/[id]` (final report — roadmap, PRD, stakeholder summary, tabs per agent's raw findings) · `/history` (past runs, for before/after comparison) |
| **Navigation Type** | Simple top navbar: Home · History. No sidebar needed — this is a small, linear tool, not a multi-section app |
| **First Screen** | Home page: a form — target URL, up to 3 competitor URLs, 1–3 target buyer queries to test citation against, "Run Audit" button |
| **Auth Flow** | None — no login. User lands directly on the form. |
| **Core User Journey 1 (first run)** | User enters target URL + competitor URLs + buyer queries → clicks Run → redirected to `/run/[id]` showing a live checklist (Technical SEO ✓ → AEO Signal ✓ → Content Strategy ✓ → Competitive Intel ✓ → PM Synthesizer ✓) → auto-redirects to `/report/[id]` when done |
| **Core User Journey 2 (before/after)** | User goes to `/history`, picks a prior run, clicks "Re-run for comparison" → new run executes against the same URL/queries → `/report/[id]` shows a diff view: citation rate before vs. after, roadmap items marked "resolved" if findings improved |
| **Empty States** | `/history` with no runs yet: "No audits run yet — start your first one" with a button back to `/`. |
| **Error States** | - Target URL unreachable → inline error on the form, don't start a run<br>- One agent fails mid-run (e.g. PageSpeed API rate-limited) → report still generates, that section shows "data unavailable" rather than blocking the whole pipeline<br>- Web search tool returns nothing for a query → AEO Signal Agent notes "no citation detected" as a valid (not error) result |
| **Redirects** | After submitting the form → `/run/[id]`. After run completes → `/report/[id]`. "Re-run" from `/history` → `/run/[id]` for the new run. |

---

## 04 — UI/UX Design Brief

| Field | Detail |
|---|---|
| **Aesthetic** | Minimal, clean, data-forward — like a lightweight internal analytics tool. Think Linear/Vercel dashboard energy, not a marketing site. |
| **Primary Color** | `#6C47FF` (indigo) — used for the primary CTA ("Run Audit") and active states |
| **Background Color** | `#0D0D0D` dark mode primary; `#FFFFFF` light mode optional |
| **Text Color** | `#F5F5F7` on dark, `#111111` on light |
| **Accent / CTA Color** | `#6C47FF`, with a secondary green (`#22C55E`) reserved specifically for "cited ✓" / positive-signal states, and red (`#EF4444`) for "not cited" / issues found — since citation status is the core signal of the whole tool, it deserves its own color language |
| **Font** | Inter for UI text, a monospace font (e.g. Geist Mono / JetBrains Mono) for URLs, schema snippets, and raw agent output |
| **Component Style** | Rounded corners (8px), flat with subtle shadows on cards only — each agent's findings live in its own card so the "5 specialists reporting in" structure is visually legible |
| **Border Radius** | 8px throughout |
| **Shadows** | Subtle card shadows only; no heavy drop shadows |
| **Dark/Light Mode** | Dark mode primary (fits the "ops tool" feel), light mode as a toggle |
| **Reference Apps** | Linear, Vercel dashboard, Ahrefs (for the data-density pattern specifically on the report page) |
| **Key UI Patterns** | - Card per agent on the report page<br>- A checklist/progress stepper on the `/run/[id]` page (5 steps, one per agent)<br>- RICE-scored roadmap rendered as a sortable table<br>- Before/after citation rate shown as a simple two-bar comparison, not a complex chart |
| **Mobile** | Should be viewable on mobile (report is often screenshotted from a phone for portfolio use) but the primary use case is desktop; no need for a dedicated mobile nav pattern beyond responsive stacking |
| **Accessibility** | Standard contrast ratios (WCAG AA), no color-only signaling for cited/not-cited (pair with ✓/✗ icons, not just green/red) |

---

## 05 — Backend Schema

| Field | Detail |
|---|---|
| **Table: runs** | `id (uuid, pk)`, `target_url (text)`, `competitor_urls (json)`, `buyer_queries (json)`, `status (text: pending/running/complete/partial/failed)`, `created_at (timestamp)`, `parent_run_id (uuid, nullable, FK → runs.id)` — set when this run is a "re-run for comparison" of an earlier one. `partial` means at least one agent failed but the PM Synthesizer still ran and produced a roadmap from whatever data was available. |
| **Table: agent_results** | `id (uuid, pk)`, `run_id (uuid, FK → runs.id)`, `agent_name (text: technical_seo / aeo_signal / content_strategy / competitive_intel / pm_synthesizer)`, `raw_output (json)`, `status (text: success/error)`, `created_at (timestamp)` |
| **Table: roadmap_items** | `id (uuid, pk)`, `run_id (uuid, FK → runs.id)`, `title (text)`, `reach (int)`, `impact (int)`, `confidence (int)`, `effort (int)`, `rice_score (float, computed)`, `description (text)`, `status (text: open/resolved)` — `status` flips to `resolved` on a comparison run if the underlying finding improved |
| **Relationships** | `agent_results.run_id → runs.id` (many-to-one) · `roadmap_items.run_id → runs.id` (many-to-one) · `runs.parent_run_id → runs.id` (self-referencing, for before/after pairs) |
| **Indexes** | Index on `agent_results.run_id`, `roadmap_items.run_id`, and `runs.parent_run_id` for fast history/comparison lookups |
| **Auth Provider** | None — no auth in v1 |
| **Row Level Security** | N/A (single-user, no auth) |
| **User Roles** | N/A (single-user) |
| **File Storage** | None needed — all output is structured JSON/text stored directly in SQLite, no binary assets |
| **Sensitive Fields** | None stored (no user PII, no payment data) — `ANTHROPIC_API_KEY` and `PAGESPEED_API_KEY` live only in environment variables, never in the DB |
| **API Endpoints** | `POST /runs` (start a new audit) · `GET /runs/{id}` (poll status/progress) · `GET /runs/{id}/report` (final structured report) · `GET /runs` (history list) · `POST /runs/{id}/rerun` (create a comparison run) |

---

## 06 — Implementation Plan

| Phase | Detail |
|---|---|
| **Phase 1: Setup** | Init monorepo (`/backend`, `/frontend`), configure `.env.example`, set up FastAPI skeleton + Next.js skeleton, confirm both run locally and can talk to each other (CORS configured). **Done when:** a hello-world API call from frontend to backend works. |
| **Phase 2: Database** | Define SQLModel schema for `runs`, `agent_results`, `roadmap_items` per Doc 05. Write init script to create local SQLite file. **Done when:** you can manually insert and query a test run via the API. |
| **Phase 3: Agent 1 — Technical SEO** | Build the schema/JSON-LD parser + PageSpeed API wrapper as tools; write the system prompt; wire a single Claude API call that takes a URL and returns structured findings (JSON). **Done when:** running it against a real URL returns a sensible, structured JSON output. |
| **Phase 4: Agent 2 — AEO Signal** | Wire Claude with the web_search tool; write the prompt to test buyer queries and detect whether the target domain is cited. **Done when:** you can test one real query and see a correct cited/not-cited result against a known page. |
| **Phase 5: Agent 3 & 4 — Content Strategy + Competitive Intel** | Content Strategy Agent takes Phase 3+4 outputs as context and proposes edits. Competitive Intel Agent reruns the Phase 4 logic against competitor URLs. **Done when:** both return structured JSON and Content Strategy's suggestions clearly reference the specific findings that prompted them. |
| **Phase 6: Agent 5 — PM Synthesizer** | Takes all four prior JSON outputs as context; produces RICE-scored roadmap, one-page PRD for the top item, and a stakeholder summary. This is the highest-value agent — spend the most prompt-iteration time here. **Done when:** output is genuinely usable as a real prioritization artifact, not a generic bullet list. |
| **Phase 7: Orchestration + API** | Wire all 5 agents into `orchestrator.py` in sequence, expose via `POST /runs`, persist each agent's result as it completes so the frontend can poll live progress. **Done when:** a full end-to-end run via API works with no manual steps. |
| **Phase 8: Frontend** | Build `/`, `/run/[id]`, `/report/[id]`, `/history` per Doc 03/04. Poll run status for the live progress view; render the report with per-agent cards + roadmap table. **Done when:** you can complete a full run through the UI without touching the terminal. |
| **Phase 9: Before/After Loop** | Implement `parent_run_id` linking and the re-run flow; add the before/after comparison view on the report page. **Done when:** you've run one real target URL twice (before/after an actual content or schema change) and the diff renders correctly. |
| **Phase 10: Polish + Deploy** | Error handling for unreachable URLs / failed agent calls, responsive layout pass, deploy backend (Railway/Render) + frontend (Vercel), write the repo README with the problem statement, architecture diagram, and your real before/after result. **Done when:** a stranger can open the deployed link (or the README) and understand what this is and why it matters in under a minute. |
| **Overall Done Criteria** | You have: a working deployed (or locally-demoable) tool, one real documented before/after citation-rate result, and a README that states the problem in the language of the job you're targeting. |

---

### Next step
Paste this whole document at the start of a Claude Code session with: *"Here are my project documents. Use these as the source of truth for everything you build, starting with Phase 1."*
