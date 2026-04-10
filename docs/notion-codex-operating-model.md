# Notion AI + Codex Operating Model for Dispatches

This document defines the working split between:

- **Notion AI** as the editorial intelligence layer
- **Codex** as the deterministic implementation and execution layer

The goal is to make the system reliable, not merely impressive.

## Core Rule

Use **Notion AI** to think across the workspace.

Use **Codex** to act on the repo and run deterministic tooling.

That gives Dispatches:

- one place for living context and editorial intelligence
- one place for implementation, validation, and publishing execution

## Ownership Split

## Notion AI Owns

Notion AI should be the primary tool for:

- mining meeting notes, transcript pages, and source materials
- clustering repeated themes and pattern signals
- drafting and refining pipeline entries
- helping classify entries by:
  - extraction mechanism
  - content tier
  - intended reader
  - narrator perspective
  - voice balance
- suggesting article angles, family guides, debugger outputs, and glossary terms
- identifying bottlenecks or gaps inside `Dispatches HQ`
- maintaining living strategy and workflow docs

In short:

**Notion AI owns editorial intelligence inside the knowledge system.**

## Codex Owns

Codex should be the primary tool for:

- reading and modifying repo files
- generating deterministic context packets
- running validation and QA scripts
- preparing publish-ready Markdown
- checking front matter and metadata consistency
- analyzing the Jekyll corpus directly
- implementing scripts that bridge Notion and the repo
- running local build or sync commands
- creating repeatable tooling for publish-readiness and corpus intelligence

In short:

**Codex owns deterministic execution and repo-side automation.**

## Shared Responsibilities

These are collaborative zones where both systems contribute:

- topic development
- family-guide conversion
- canon-building
- pattern analysis
- social-signal triage

The difference is where each part happens:

- Notion AI handles the upstream interpretation
- Codex handles the downstream implementation and verification

## Handoff Model

## Handoff 1: Internal Intelligence -> Pipeline

**Owner:** Notion AI

Inputs:

- meeting notes
- transcript pages
- source material
- prior drafts
- TELOS and voice docs

Output:

- a structured pipeline item with:
  - title or working angle
  - signal summary
  - extraction mechanism
  - content tier
  - intended reader
  - suggested format
  - editorial notes

This should happen entirely inside Notion whenever possible.

## Handoff 2: Pipeline -> Draft Plan

**Owner:** Notion AI first, Codex second

Notion AI should produce:

- draft scaffold
- target audience framing
- family translation layer where needed
- source checklist

Codex should then use:

- the repo context
- existing canon
- current front matter conventions
- local scripts

to prepare a repo-aware drafting or editing session.

## Handoff 3: Draft -> Repo Implementation

**Owner:** Codex

This is where Codex takes over.

Tasks:

- create or edit the Markdown file
- align front matter with site conventions
- preserve redirects and URL behavior
- check internal links and categories
- run deterministic QA

Notion AI should not be the source of truth for these repo-side mechanics.

## Handoff 4: Published Artifact -> Learning

**Owner:** both

Codex side:

- capture repo-safe lessons
- update scripts or docs when recurring issues appear

Notion side:

- update workflow docs
- track performance and signal quality
- refine prompt and classification habits

## External Signal Workflow

This is the best split for outside intelligence, including social signals.

## Step 1: External Intake

**Owner:** manual capture first, automation later

Good sources:

- Reddit
- LinkedIn
- YouTube transcripts
- selected policy or reporting sources

Capture fields:

- source
- date
- link
- signal snippet
- why it matters
- likely audience
- confidence level

Best home:

- a Notion intake page or database

## Step 2: Signal Interpretation

**Owner:** Notion AI

Tasks:

- classify the signal
- compare it to existing patterns
- decide whether it indicates:
  - a myth to decode
  - a family guide
  - a clinician-validation piece
  - a debugger output
  - a policy-analysis angle
  - noise

## Step 3: Validation

**Owner:** shared

Notion AI:

- compare with workspace sources and prior content

Codex:

- compare against repo canon
- support source-pack generation when needed
- help build structured research or QA tooling

## Step 4: Output Routing

**Owner:** Notion AI first

Possible destinations:

- new pipeline entry
- update to an existing draft
- evidence note
- glossary candidate
- debugger-rule candidate

Codex only gets involved once a signal is moving toward repo implementation or deterministic checking.

## What Notion AI Should Not Own

Avoid using Notion AI as the primary layer for:

- file-level repo editing
- Jekyll-specific front matter enforcement
- local build validation
- deterministic publish QA
- direct local execution

Those jobs belong to Codex.

## What Codex Should Not Own

Avoid using Codex as the primary layer for:

- broad workspace pattern-mining when the material is already in Notion
- daily curation of raw notes or meeting intelligence
- maintaining the live editorial dashboard as the central planning surface

Those jobs belong to Notion AI.

## Recommended Operating Rhythm

## Daily

Use Notion AI to:

- triage new ideas
- classify signals
- refine active pipeline entries

Use Codex to:

- work on repo-bound drafts
- run QA and publishing checks

## Weekly

Use Notion AI to:

- review content bottlenecks
- identify under-served audiences or tiers
- process social and external signals

Use Codex to:

- generate corpus intelligence from `_posts/`
- update deterministic tools
- support any structured publishing batch

## Monthly

Use Notion AI to:

- audit strategy, voice drift, and pipeline health

Use Codex to:

- improve scripts
- tighten validation rules
- refresh context tooling

## Immediate Next Implementation

The clean next stack would be:

1. create a Notion social-signal intake structure
2. use Notion AI to classify and route those signals
3. use Codex to build:
   - `editorial_qa.py`
   - a corpus-to-canon helper
   - a source-pack or context-pack helper where useful

## Decision Rule

When deciding where a task belongs, ask:

### If the task is mainly:

- interpretation
- classification
- mining workspace context
- developing editorial direction

Use **Notion AI**.

### If the task is mainly:

- execution
- file editing
- deterministic validation
- build and publish mechanics

Use **Codex**.

## Short Version

**Notion AI is the editorial brain.**

**Codex is the execution engine.**

**The pipeline between them is the real system.**
