# Morning Sweep — Setup Guide

## Required APIs

### Gmail
- OAuth 2.0 credentials from Google Cloud Console
- Scopes: gmail.readonly, gmail.modify
- Token file: ~/.openclaw/workspace/.credentials/gmail_token.json

### Google Calendar
- Same Google Cloud project as Gmail
- Scopes: calendar.readonly, calendar.events
- Reuses gmail_token.json if same account

### Todoist
- Personal API token from todoist.com/app/settings/integrations
- Store in: ~/.openclaw/workspace/.env.todoist
- `TODOIST_API_TOKEN=your_token_here`

## Installation

```bash
pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client todoist-api-python
```

## First Run (Auth)

```bash
cd /Users/dron/.openclaw/workspace
python3 morning_sweep.py --setup
# Opens browser for Google OAuth
# Saves token to .credentials/gmail_token.json
```

## Cron Setup

```bash
# Run overnight triage at 6 AM EST daily
0 6 * * * cd /Users/dron/.openclaw/workspace && python3 morning_sweep.py --mode email >> /tmp/morning_sweep.log 2>&1
```
