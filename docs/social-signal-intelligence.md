# Social Signal Intelligence for Dispatches

This document defines how to use social media as an intelligence source for Dispatches from Discharge Hell.

The goal is not to treat social media as authority.

The goal is to use it as a **signal-detection layer** for:

- emerging family confusion
- repeated clinician frustrations
- payer and post-acute talking points
- language shifts
- new pattern clusters worth validating elsewhere

## Core Principle

Social media should be treated as **early warning radar**, not proof.

Use it to detect:

- what people are asking
- what people are misunderstanding
- what people are normalizing
- what professionals are quietly admitting
- what narratives are spreading before formal reporting catches up

Then validate against:

- your own lived pattern archive
- Notion source materials
- public reporting
- policy or regulatory sources
- published research where relevant

## Why This Fits the Miessler Pattern

This is the closest analog in your domain to how Miessler uses outside intelligence.

He is not just browsing randomly. He is:

- collecting external signals
- routing them into structured analysis
- comparing them to internal context
- deciding whether the signal should change the system

For Dispatches, social media should do the same thing:

- collect external signals
- compare them to your internal case-pattern knowledge
- decide whether they indicate:
  - a publishable post
  - a family guide
  - a myth to debunk
  - a new glossary term
  - a future debugger rule

## Best Source Types

### 1. Reddit

Highest-value subreddits are likely:

- caregiver support communities
- TBI / SCI / stroke / rehab communities
- insurance and billing frustration communities
- nursing and case management communities

Why it matters:

- best source for the "2 AM reader"
- strongest raw language for confusion, panic, and false assumptions
- good for spotting recurring family questions

Use for:

- family-facing explainer ideas
- glossary entries
- "what this usually means" posts
- debugger translations

### 2. LinkedIn

Best for:

- clinician frustration signals
- discharge planning and utilization-management discourse
- hospital / payer / post-acute talking points
- adjacent healthcare policy and leadership narratives

Why it matters:

- professionals reveal what is becoming discussable in public
- helps track how institutions frame the same problems you see operationally

Use for:

- policy-analysis pieces
- clinician-validation posts
- contrast between operational reality and public-facing language

### 3. YouTube

Useful signal sources:

- healthcare commentary
- patient and caregiver channels
- policy interviews
- industry discussions
- conference talks

Why it matters:

- high-signal long-form narratives
- transcript-friendly
- good source for language shifts and public framing

Use for:

- transcript mining
- quote banks
- response posts
- theme clustering

### 4. X / short-form public commentary

Use carefully.

Strengths:

- fast narrative detection
- useful for trend and language monitoring

Weaknesses:

- low reliability
- high outrage distortion
- weak evidence density

Use for:

- tracking phrase emergence
- spotting misinformation themes
- watching issue velocity

Do not use it as stand-alone evidence.

## Signal Types to Track

Every social signal should be classified into one or more of these buckets.

### Family confusion

Examples:

- "why are they sending my dad home already?"
- "what does medical necessity actually mean?"
- "they said rehab but now they say SNF"

Likely outputs:

- family guide
- glossary
- Start Here update
- debugger translation phrase

### Clinician validation

Examples:

- case managers describing the same bottleneck
- bedside nurses naming discharge absurdities
- rehab professionals confirming operational patterns

Likely outputs:

- peer-insight post
- system-pattern explainer
- canon support for existing claims

### Institutional narrative

Examples:

- payer language trends
- hospital leadership framing
- post-acute marketing language
- "patient-centered" messaging that obscures incentives

Likely outputs:

- policy analysis
- language deconstruction post
- satire with stronger evidence spine

### Failure-mode signal

Examples:

- repeated issues around DME
- home health delay patterns
- LTAC / SNF confusion
- appeals misunderstandings
- family-capacity collapse

Likely outputs:

- debugger rule
- checklist
- decision tree
- operational explainer

### Moral-injury signal

Examples:

- professionals naming burnout, compromise, and silent compliance
- families describing institutional betrayal

Likely outputs:

- persona / witness essay
- workforce layer analysis
- human-cost counter content

## Social Signal Workflow

### Step 1: Capture

Capture the raw signal with:

- platform
- link
- date
- snippet
- audience type
- why it stood out

### Step 2: Classify

Assign:

- signal type
- extraction mechanism
- likely audience
- confidence level
- urgency

### Step 3: Compare

Ask:

- have we seen this pattern internally?
- is this new, or is it confirming something old?
- does it contradict existing assumptions?
- is it specific enough to matter?

### Step 4: Validate

Before turning it into a public claim:

- compare with existing posts
- compare with Notion source materials
- compare with research / policy / reporting if needed

### Step 5: Route

Choose one destination:

- create or update pipeline entry
- attach to existing draft as evidence or audience signal
- store as weak signal only
- discard as noise

## Suggested Output Types

These are the best outputs social media should feed.

### 1. Myth / Translation posts

Format:

- what they said
- what families think it means
- what it usually means operationally

### 2. Family debugger blocks

Format:

- where you are
- what's happening
- what to ask next
- what to document
- red flags

### 3. Clinician-validation posts

Format:

- here is the pattern
- here is why the system produces it
- here is who gets blamed

### 4. Pattern alerts

Format:

- repeated new signal
- why it matters now
- whether the canon already covers it

## Guardrails

### Do not confuse salience with prevalence

A loud signal is not automatically a common one.

### Do not quote identifiable patient situations carelessly

Keep the same privacy posture you use elsewhere.

### Do not let social media define the editorial agenda by itself

It should influence priorities, not replace judgment.

### Do not publish claims sourced only from social chatter

Use social signals to generate hypotheses, not final evidence.

### Do not optimize for outrage

The brand promise is clarity and field literacy, not engagement bait.

## First Practical Implementation

The first useful version does not need API automation.

Start with a recurring manual or AI-assisted workflow:

1. review a bounded set of sources weekly
2. capture 5-10 signals
3. classify them
4. convert the best 1-2 into pipeline items or evidence notes
5. discard the rest

That keeps the system high-signal and prevents infinite intake.

## Best Initial Weekly Queries

These are examples of the kinds of searches worth testing.

### Family-side

- rehab denied insurance
- skilled nursing facility after rehab confusion
- home health not enough help
- discharge too soon hospital insurance
- medical necessity denial rehab

### Clinician-side

- case management discharge planning frustration
- prior authorization rehab denial
- SNF placement no bed available
- DME discharge delay
- home health agency no staffing

### System-side

- utilization management rehab
- payer medical necessity post acute
- LTAC rehab discharge planning
- Medicare Advantage rehab denial

## Recommended Notion Routing

If you want this to become operational inside your current system, create or use fields like:

- `Signal Source`
- `Signal Type`
- `External Signal Summary`
- `Validation Status`
- `Social Signal Priority`

And route validated items into the existing `Master Content Pipeline`.

## What to Build Next

The best next implementation step would be a lightweight intake structure, not a full crawler.

Suggested sequence:

1. define a social-signal note template in Notion
2. create one weekly signal review ritual
3. add one deterministic helper to convert saved signals into pipeline-ready summaries
4. only then consider automation per platform
