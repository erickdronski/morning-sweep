# Morning Sweep — AI-Powered Personal Chief of Staff

> Triages your inbox, calendar, and tasks before you wake up. Delivers a structured day in minutes.

---

## What It Does

Morning Sweep is a multi-agent AI system that runs while you sleep. By the time you pour your first coffee, it has already:

- Scanned your inbox and identified what needs action
- Reviewed your calendar for conflicts and back-to-backs
- Classified every item into one of four buckets: `dispatch / prep / yours / skip`
- Drafted emails, resolved scheduling conflicts, and compiled research — all autonomously
- Delivered a clean briefing to Discord so your day is ready before you are

---

## The Framework

```
dispatch / prep / yours / skip

🟢 dispatch — Agent handles 100% autonomously
🟡 prep     — Agent gets it 80% ready, you review
🔴 yours    — Needs your brain or presence
⚫ skip     — Not actionable today, deferred
```

The classification is the core of the system. Claude reasons over each item and decides which bucket it belongs in. When in doubt, it biases toward `prep` — never claiming more autonomy than it's earned.

---

## Architecture

```
Gmail + Google Calendar + Todoist
           │
           ▼
    [Triage Agent] (6 AM, overnight)
    - Scans inbox, identifies action items
    - Scans calendar for conflicts + back-to-backs
    - Creates Todoist tasks with metadata
           │
           ▼
    [Morning Sweep Agent] (on-demand)
    - Pulls all tasks + calendar context
    - Classifies: dispatch / prep / yours / skip
    - Fires specialized sub-agents in parallel:
      ├── Email Drafter (drafts only, never sends)
      ├── Calendar Manager (schedules/reschedules)
      ├── Researcher (background on topics/people)
      └── Note-taker (updates workspace files)
           │
           ▼
    [Completion Report] → Discord notification
```

The triage agent runs on a cron schedule (6 AM). The morning sweep agent runs on-demand — typically when you sit down to start your day. Results land in Discord as a structured briefing.

---

## Sample Output

```
🌅 Morning Sweep — Monday, March 30, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Inbox: 14 emails scanned | 4 action items found
📅 Calendar: 3 meetings today | 1 conflict detected
✅ Tasks: 7 open | 2 due today

🟢 DISPATCH (agent handles)
  • Respond to Amanda re: Tuesday availability → drafted & queued
  • Reschedule 2PM → 3PM (conflict with standup) → updated

🟡 PREP (80% ready for you)
  • Email: Ivanti QBR follow-up → draft in inbox, needs your review
  • Research: Background on Johnson & Johnson account → notes compiled

🔴 YOURS (needs your brain)
  • Strategic: PA pricing decision for enterprise tier
  • Personal: Response to Laura's calendar request

⚫ SKIP (deferred)
  • Newsletter feedback request → low priority, deferred to Thursday

⏱️ Your focus time: 9-11 AM (blocked), 2-4 PM (blocked)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| AI reasoning | Anthropic Claude API |
| Email | Gmail API (OAuth 2.0) |
| Calendar | Google Calendar API |
| Tasks | Todoist REST API |
| Orchestration | [OpenClaw](https://openclaw.io) |
| Notifications | Discord webhook |
| Runtime | Python 3.x |

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/erickdronski/morning-sweep
cd morning-sweep
pip install -r requirements.txt
```

### 2. Set up credentials

```bash
cp .env.example .env
# Fill in your API keys — see references/setup.md for OAuth flows
```

### 3. Run the demo

```bash
ANTHROPIC_API_KEY=your_key_here python morning_sweep.py
```

The demo uses mock data — no Gmail/Calendar/Todoist credentials needed. It shows the full classification pipeline and prints a formatted morning briefing.

---

## Rules

The system operates under a strict set of constraints to stay trustworthy:

- **Never sends emails autonomously** — always drafts for human review
- **Personal and family communications** are always flagged as `yours`
- **Strategic business decisions** are always flagged as `yours`
- **Bias toward `prep` over `dispatch`** when classification is uncertain
- **Calendar changes are logged** before they're made, with a rollback path

These aren't just suggestions — they're baked into the classification prompt.

---

## Repo Structure

```
morning-sweep/
├── morning_sweep.py      # Core demo script — start here
├── requirements.txt      # Python dependencies
├── references/
│   └── setup.md          # OAuth setup guides (Gmail, Calendar, Todoist)
└── SKILL.md              # OpenClaw skill definition
```

---

## Status

This is a working concept being actively used and refined. The demo script (`morning_sweep.py`) is fully runnable with just an Anthropic API key. Full API integrations (Gmail, Calendar, Todoist) are documented in `references/setup.md`.

---

## License

MIT
