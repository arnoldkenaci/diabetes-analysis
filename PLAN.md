# ✅ Project Checklist: Automated Dataset Analysis Web App

## Phase 1: Planning & Setup

- [x] Create project folder structure (`backend/`, `frontend/`, `docs/`)
- [x] Initialize Git repository
- [x] Set up `.gitignore` for Python, Node, etc.
- [x] Create `README.md` with goals and setup steps
- [x] Choose tech stack:
  - [x] Backend: Python (FastAPI or Flask): FastAPI
  - [x] Frontend: React / Vue / Angular: React
  - [x] Database: PostgreSQL
  - [x] Notification: Email or Slack: Slack
  - [x] LLM API: (e.g., OpenRouter, Hugging Face): Hugging Face

---

## Phase 2: Data Layer

- [x] Download or generate dummy dataset
- [x] Design PostgreSQL schema
- [x] Set up local PostgreSQL DB
- [x] Write data import script to load dataset into DB

---

## Phase 3: Backend Development

- [x] Set up backend with FastAPI or Flask
- [x] Connect to PostgreSQL
- [x] Create REST API endpoints:
  - [x] `/data` - Get dataset (with filters)
  - [x] `/analyze` - Run analysis
  - [x] `/insights` - Fetch insights
- [x] Implement analysis logic:
  - [x] Anomaly detection
  - [x] KPI calculations (e.g., ROI, CTR)
  - [x] Trend summaries
- [x] Set up scheduled/triggered analysis (e.g., cron, APScheduler)

---

## Phase 4: Notifications

- [x] Integrate email or Slack API
- [x] Send alerts only on meaningful findings
- [x] Format notification with:
  - [x] Summary of findings
  - [x] Link to dashboard
  - [x] Recommendations

---

## Phase 5: LLM Integration

- [x] Choose a free LLM API
- [x] Generate:
  - [x] Natural language summaries
  - [x] Actionable recommendations
- [x] Add safeguards (rate limiting)

---

## Phase 6: Frontend Development

- [x] Set up React
- [x] Build interactive dashboard:
  - [x] Dataset table with filters/sorting
  - [x] Highlight significant data points
  - [x] Display AI-generated insights
- [x] Connect to backend via API
- [x] Add basic routing if needed

---

## Phase 7: Testing & Finalization

- [ ] Unit tests for backend logic
- [ ] Test LLM integration with mock + real data
- [ ] Test notifications (email/Slack)
- [ ] Full flow test: Data → Analysis → Notify → Dashboard

---

## Phase 8: Documentation & Packaging

- [ ] Finalize `README.md`:
  - [ ] Setup instructions
  - [ ] API docs
  - [ ] Walkthrough
- [ ] Add code comments and cleanup
- [x] (Optional) Add Docker setup for backend/frontend

---

## Optional Additions

- [ ] User authentication (e.g., JWT)
- [x] Dataset upload feature via UI
- [x] Export dashboard to PDF
- [ ] Historical insight comparison
- [x] Add charts (Chart.js, Recharts, etc.)
