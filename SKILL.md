---
name: morning-sweep
description: "AI-powered morning operations system. Triages email, calendar, and tasks before the user wakes up, then classifies them into dispatch/prep/yours/skip. Use when setting up or running the daily morning briefing system, automating inbox triage, or building a personal chief-of-staff workflow. Integrates with Gmail, Google Calendar, and Todoist."
---

# Morning Sweep

A personal chief-of-staff system that runs before you wake up and gives you a structured day in minutes.

## The Framework: dispatch / prep / yours / skip

Every task gets classified into one of four buckets:

| Color | Label | Meaning | Agent Action |
|-------|-------|---------|-------------|
| 🟢 | dispatch | Agent handles 100% autonomously | Execute and mark done |
| 🟡 | prep | Agent gets it 80% ready | Draft/prep, flag for review |
| 🔴 | yours | Needs Erick's brain or presence | Flag with context assembled |
| ⚫ | skip | Not actionable today | Defer with reason + suggested date |

**Bias rule:** When uncertain, default to prep (🟡) over dispatch (🟢). Never send emails autonomously — always draft for review.

## System Components

**Layer 1 (overnight, ~6 AM):**
- Email triage: scan inbox, identify action items, create Todoist tasks with metadata
- Calendar scan: identify conflicts, calculate drive times, flag back-to-back issues

**Layer 2 (morning, on demand — "AM Sweep"):**
- Pull all Todoist tasks + calendar context
- Classify each task: dispatch / prep / yours / skip
- Fire specialized sub-agents in parallel:
  - Email drafter (drafts only, never sends)
  - Calendar manager (schedules, reschedules)
  - Researcher (background research on topics/people)
  - Note-taker (updates Obsidian/workspace files)
- Deliver completion report

**Layer 3 (time blocking — "Time Block"):**
- Convert remaining tasks to time-blocked calendar events
- Batch errands geographically (minimize backtracking)
- Schedule focused work in peak energy windows (9-11 AM, 2-4 PM)
- Protect Erick's strategic thinking time

## Running the Sweep

```bash
# Full morning sweep
cd /Users/dron/.openclaw/workspace
python3 morning_sweep.py --mode full

# Just email triage
python3 morning_sweep.py --mode email

# Just time blocking
python3 morning_sweep.py --mode timeblock
```

## What Stays Human (Non-Negotiable)

- Sending emails (agent drafts, Erick sends)
- Strategic decisions on Ivanti/Precision Algorithms
- Pricing, negotiation, relationship-sensitive comms
- Anything touching Laura, family, personal finances

## Setup Requirements

See `references/setup.md` for Gmail OAuth, Google Calendar API, and Todoist token configuration.
