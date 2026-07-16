# AEO Product Ops System

A multi-agent system that audits, tests, and prioritizes what to fix for AI-answer-engine visibility — built to explore how product management works when "search" means being cited by ChatGPT/Perplexity/AI Overviews instead of ranking on a results page.

## The problem

A growing share of search queries now get answered directly by AI, with no click-through to a website. Companies have spent 20 years optimizing for traditional ranking factors, but there's no simple, repeatable way to measure whether a page is actually structured to be *cited* by an AI answer engine, or to turn that signal into a prioritized action plan the way SEO tools have long done for search ranking.

## What this does

Simulates a small cross-functional product team as five Claude-powered agents:

1. **Technical SEO Agent** — checks schema markup, meta tags, Core Web Vitals
2. **AEO Signal Agent** — tests real buyer queries to see if the target page gets cited by AI search
3. **Content Strategy Agent** — proposes specific content fixes based on the findings
4. **Competitive Intel Agent** — runs the same citation tests against competitors
5. **PM Synthesizer Agent** — turns all four agents' (often conflicting) findings into one RICE-scored, prioritized roadmap + a one-page PRD for the top item

The system closes the loop: re-run it after a fix ships to see whether citation behavior actually changed, with real before/after data — not just a one-time audit.

## Status

🚧 In progress — see `/docs/project-docs.md` for the full PRD, technical spec, and build plan.

## Stack

Python (FastAPI) + Next.js, calling the Anthropic API directly — no agent framework dependency.

## Setup

```bash
cp .env.example .env   # add your API keys
```

(Full setup instructions coming as the build progresses.)
