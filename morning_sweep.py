"""
Morning Sweep — AI-Powered Personal Chief of Staff
Pattern: Multi-agent triage with parallel specialized sub-agents
Use case: Classify and prepare your day before you start it

This script demonstrates the core dispatch/prep/yours/skip framework
using Claude as the reasoning layer for task classification.

Run it:
    ANTHROPIC_API_KEY=your_key python morning_sweep.py

No Gmail/Calendar/Todoist credentials needed — uses mock data.
"""

import json
import os
from datetime import datetime
from typing import Literal

import anthropic

# ─── Classification buckets ───────────────────────────────────────────────────

Classification = Literal["dispatch", "prep", "yours", "skip"]

CLASSIFICATION_DESCRIPTIONS = {
    "dispatch": "Agent handles 100% autonomously",
    "prep":     "Agent gets it 80% ready, you review",
    "yours":    "Needs your brain or presence",
    "skip":     "Not actionable today, deferred",
}

# ─── Mock data ────────────────────────────────────────────────────────────────

MOCK_INBOX = [
    {
        "id": "email_001",
        "from": "amanda@example.com",
        "subject": "Tuesday availability?",
        "preview": "Hi, are you free Tuesday 2pm for a quick sync?",
    },
    {
        "id": "email_002",
        "from": "boss@company.com",
        "subject": "Q2 strategy doc",
        "preview": "Please review by EOD and add your section on enterprise pricing.",
    },
    {
        "id": "email_003",
        "from": "newsletter@substack.com",
        "subject": "Weekly digest",
        "preview": "Top stories this week in AI and fintech...",
    },
    {
        "id": "email_004",
        "from": "laura@family.com",
        "subject": "Dinner this weekend?",
        "preview": "Hey, are you free Saturday? Mom wants everyone over.",
    },
    {
        "id": "email_005",
        "from": "ivanti-account@ivanti.com",
        "subject": "QBR follow-up action items",
        "preview": "Per our call, here are the three items we agreed to address by next week.",
    },
]

MOCK_CALENDAR = [
    {"time": "9:00 AM", "title": "Standup", "duration_min": 30},
    {"time": "2:00 PM", "title": "Client call — Johnson & Johnson", "duration_min": 60},
    {"time": "2:00 PM", "title": "Team sync", "duration_min": 30},  # conflict!
    {"time": "4:00 PM", "title": "1:1 with boss", "duration_min": 45},
]

MOCK_TASKS = [
    {"id": "task_001", "title": "PA pricing decision for enterprise tier", "due": "today", "priority": 1},
    {"id": "task_002", "title": "Follow up with Ivanti on QBR items", "due": "today", "priority": 2},
    {"id": "task_003", "title": "Read Q2 strategy doc", "due": "today", "priority": 2},
    {"id": "task_004", "title": "Book flights for April offsite", "due": "this week", "priority": 3},
    {"id": "task_005", "title": "Review newsletter feedback", "due": "this week", "priority": 4},
]

# ─── Classification system ─────────────────────────────────────────────────────

CLASSIFICATION_SYSTEM_PROMPT = """You are the Morning Sweep triage agent. Your job is to classify each item
into one of four buckets based on what's needed to handle it:

- dispatch: Agent can handle 100% autonomously. Simple scheduling, standard replies, low-stakes tasks.
- prep: Agent does 80% of the work, but human needs to review before it goes out. Draft emails, research memos.
- yours: Requires human judgment, presence, or relationships. Strategic decisions, personal communications, anything sensitive.
- skip: Not actionable today. Low priority, no deadline pressure, or blocked on something external.

Hard rules — always apply:
1. Personal or family communications → always "yours"
2. Strategic business decisions → always "yours"  
3. Anything you're not 100% confident about → bias toward "prep" not "dispatch"
4. Newsletters, digests, non-actionable FYIs → "skip"

Respond with JSON only. Format:
{
  "classification": "dispatch|prep|yours|skip",
  "reason": "one sentence explaining why",
  "suggested_action": "what should happen next"
}"""


def classify_item(client: anthropic.Anthropic, item_type: str, item: dict) -> dict:
    """Use Claude to classify a single inbox/calendar/task item."""

    item_description = json.dumps(item, indent=2)

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=256,
        system=CLASSIFICATION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Classify this {item_type}:\n\n{item_description}",
            }
        ],
    )

    raw = message.content[0].text.strip()

    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)
    result["item"] = item
    result["type"] = item_type
    return result


# ─── Conflict detection ────────────────────────────────────────────────────────

def detect_calendar_conflicts(calendar: list[dict]) -> list[tuple]:
    """Find overlapping calendar events."""
    conflicts = []
    times = {}
    for event in calendar:
        t = event["time"]
        if t in times:
            conflicts.append((times[t], event))
        else:
            times[t] = event
    return conflicts


# ─── Report formatter ──────────────────────────────────────────────────────────

def format_report(classified_items: list[dict], conflicts: list[tuple], date_str: str) -> str:
    """Format classified items into the morning briefing."""

    buckets = {"dispatch": [], "prep": [], "yours": [], "skip": []}
    for item in classified_items:
        buckets[item["classification"]].append(item)

    inbox_count = sum(1 for i in classified_items if i["type"] == "email")
    action_count = sum(1 for i in classified_items if i["type"] == "email" and i["classification"] != "skip")
    meeting_count = sum(1 for i in classified_items if i["type"] == "calendar_event")
    task_count = sum(1 for i in classified_items if i["type"] == "task")
    due_today = sum(1 for i in classified_items if i["type"] == "task" and i["item"].get("due") == "today")

    lines = [
        f"🌅 Morning Sweep — {date_str}",
        "━" * 42,
        "",
        f"📊 Inbox: {inbox_count} emails scanned | {action_count} action items found",
        f"📅 Calendar: {meeting_count} meetings today | {len(conflicts)} conflict(s) detected",
        f"✅ Tasks: {task_count} open | {due_today} due today",
        "",
    ]

    icons = {"dispatch": "🟢", "prep": "🟡", "yours": "🔴", "skip": "⚫"}
    labels = {
        "dispatch": "DISPATCH (agent handles)",
        "prep":     "PREP (80% ready for you)",
        "yours":    "YOURS (needs your brain)",
        "skip":     "SKIP (deferred)",
    }

    for bucket in ["dispatch", "prep", "yours", "skip"]:
        items = buckets[bucket]
        if not items:
            continue
        lines.append(f"{icons[bucket]} {labels[bucket]}")
        for item in items:
            action = item.get("suggested_action", "—")
            lines.append(f"  • {action}")
        lines.append("")

    if conflicts:
        lines.append("⚠️  CONFLICTS DETECTED")
        for a, b in conflicts:
            lines.append(f"  • {a['time']}: {a['title']} vs {b['title']}")
        lines.append("")

    # Find focus blocks (times with no meetings)
    meeting_times = {e["time"] for e in MOCK_CALENDAR}
    lines.append("⏱️  Your focus time: check calendar for open blocks")

    return "\n".join(lines)


# ─── Main ──────────────────────────────────────────────────────────────────────

def run_morning_sweep():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set — running in offline demo mode\n")
        print("Set ANTHROPIC_API_KEY to run live classification via Claude.\n")
        # Show a pre-baked sample output
        print(SAMPLE_OUTPUT)
        return

    client = anthropic.Anthropic(api_key=api_key)

    print("🌅 Morning Sweep starting...\n")

    # Detect calendar conflicts
    conflicts = detect_calendar_conflicts(MOCK_CALENDAR)

    # Classify all items
    classified = []

    print("📬 Classifying inbox...")
    for email in MOCK_INBOX:
        result = classify_item(client, "email", email)
        classified.append(result)
        icon = {"dispatch": "🟢", "prep": "🟡", "yours": "🔴", "skip": "⚫"}[result["classification"]]
        print(f"  {icon} [{result['classification']:8s}] {email['subject']}")

    print("\n📅 Classifying tasks...")
    for task in MOCK_TASKS:
        result = classify_item(client, "task", task)
        classified.append(result)
        icon = {"dispatch": "🟢", "prep": "🟡", "yours": "🔴", "skip": "⚫"}[result["classification"]]
        print(f"  {icon} [{result['classification']:8s}] {task['title']}")

    # Add calendar events (classified as context, not action items)
    for event in MOCK_CALENDAR:
        classified.append({
            "classification": "yours",
            "reason": "Meeting attendance",
            "suggested_action": f"Attend: {event['title']} at {event['time']}",
            "item": event,
            "type": "calendar_event",
        })

    # Format and print the report
    date_str = datetime.now().strftime("%A, %B %-d, %Y")
    report = format_report(classified, conflicts, date_str)

    print("\n" + "═" * 42)
    print(report)
    print("═" * 42)
    print("\n✅ Morning Sweep complete.")


# ─── Offline sample output ─────────────────────────────────────────────────────

SAMPLE_OUTPUT = """
🌅 Morning Sweep — Monday, March 30, 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Inbox: 5 emails scanned | 4 action items found
📅 Calendar: 4 meetings today | 1 conflict detected
✅ Tasks: 5 open | 3 due today

🟢 DISPATCH (agent handles)
  • Reply to amanda@example.com confirming Tuesday 2pm availability

🟡 PREP (80% ready for you)
  • Draft response to Ivanti QBR follow-up — ready for your review
  • Research memo on Johnson & Johnson account — compiled in notes

🔴 YOURS (needs your brain)
  • Strategic: PA pricing decision for enterprise tier — needs your call
  • Personal: Dinner reply to laura@family.com — family, not delegatable
  • Q2 strategy doc — add your section before EOD

⚫ SKIP (deferred)
  • Newsletter digest — no action needed, informational only
  • Book flights for April offsite — not due today

⚠️  CONFLICTS DETECTED
  • 2:00 PM: Client call — Johnson & Johnson vs Team sync

⏱️  Your focus time: check calendar for open blocks
"""


if __name__ == "__main__":
    run_morning_sweep()
