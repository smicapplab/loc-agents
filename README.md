# Personal AI Agents Collection

A repository for autonomous AI agents designed to automate personal workflows, research, and productivity tasks.

## Agents

### [PH Job-Seek Agent](./job-seek)
An autonomous agent that scrapes job boards (LinkedIn, Indeed, Seek, RemoteOK, WWR), filters them against a personal resume using AI (OpenAI or Gemini), and sends a curated daily email.

**Run:** `./scripts/job-seek.sh search`

### [Job-Filter Agent](./job-filter)
An agent that monitors Gmail for job alerts, extracts listings using AI, filters by salary, and scores them against a candidate profile.

**Run:** `./scripts/job-filter.sh`

---

## Configuration
All agents use a single source of truth for configuration located in the root `.env` file. See `.env.example` for required variables.

## Getting Started
1. Install dependencies: `cd job-seek && pip install -r requirements.txt`
2. Set up your `.env` in the root (see `.env.example`).
3. Place your resume at `job-seek/data/resume.pdf`.
4. Initialize your profile: `./scripts/sync.sh`
5. Use the scripts in `./scripts/` to run the agents.
