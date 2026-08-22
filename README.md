# ResumeIQ

Transparent resume ↔ job description compatibility analysis, built with classical
NLP — TF-IDF, cosine similarity and explicit skill matching. **No LLM, no external
AI API.** Every number in the final score can be traced back to the source text.

> **Status:** Phase 1 of 10 complete (Foundation).

---

## Why this exists

Most "ATS score" tools give you a single opaque percentage. ResumeIQ breaks the
score into components you can audit:

```
Overall Score = 40% Text Similarity
              + 40% Skill Match
              + 20% Keyword Match
```

…and shows you exactly which skills matched, which are missing, and which
keywords from the job description never appear in the resume.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, TypeScript, Tailwind CSS v4, React Router, Axios |
| Backend | Python 3.11, FastAPI, Pydantic v2 |
| Database | MySQL 9, SQLAlchemy 2, Alembic |
| NLP / ML | scikit-learn, spaCy, pandas, NumPy, PyMuPDF *(Phase 3+)* |

---

## Architecture

```
Browser (React, :5173)
        │  Axios
        ▼
FastAPI (:8000)
        │
   ┌────┴──────────────┬──────────────┐
   ▼                   ▼              ▼
Resume processing  Job analysis   User data
   │                   │              │
   └────────┬──────────┘              │
            ▼                         │
      NLP / ML engine                 │
            │                         │
            ▼                         │
      Match analysis ─────────────────┘
            │
            ▼
      MySQL (SQLAlchemy) ◄── Alembic migrations
```

### Backend layout

```
backend/app/
├── api/routes/     HTTP layer only — no business logic
├── core/           configuration
├── db/             engine, session, declarative base
├── models/         SQLAlchemy tables
├── schemas/        Pydantic request/response contracts
├── repositories/   database read/write helpers
└── services/       the actual thinking (auth, resume, nlp, matching, analysis)
```

The point of this split: `services/matching/` will contain the TF-IDF and cosine
similarity code with zero knowledge of HTTP or SQL, which makes it directly
unit-testable.

---

## Getting started

### Ports

ResumeIQ runs on **8001** (backend) and **5174** (frontend) rather than the usual
8000/5173, to avoid colliding with other local projects.

### Prerequisites

- Python 3.11+
- Node.js 20+
- MySQL 8 or 9, running locally

### 1. Database

```bash
mysql -u root -p < backend/scripts/init_db.sql
```

Creates the `resume_analyzer` database and a least-privilege `resumeiq` user.

### 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit DATABASE_URL if you changed credentials
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

API: <http://localhost:8001> · Interactive docs: <http://localhost:8001/docs>

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App: <http://localhost:5174>

---

## Tests

```bash
cd backend && .venv/bin/pytest -q
```

```bash
cd frontend && npm run build
```

---

## API (Phase 1)

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | service metadata |
| `GET` | `/api/health` | liveness — is the process up? |
| `GET` | `/api/health/db` | readiness — can it reach MySQL? |

Auth, resume, job and analysis endpoints arrive in Phases 2–5.

---

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Foundation: React + FastAPI + MySQL + Alembic | ✅ Done |
| 2 | Auth: JWT, password hashing, Google Sign-In | ⬜ |
| 3 | Resume upload + PDF text extraction | ⬜ |
| 4 | NLP: preprocessing, skill dictionary, extraction | ⬜ |
| 5 | Matching engine: TF-IDF, cosine similarity, scoring | ⬜ |
| 6 | Results dashboard + charts | ⬜ |
| 7 | User history + resume versioning | ⬜ |
| 8 | *Optional* supervised classifier — only with a real dataset | ⬜ |
| 9 | *Optional* local sentence-transformer semantic similarity | ⬜ |
| 10 | Testing, security, Docker, deployment | ⬜ |

---

## Security notes

- `.env` files are gitignored; only `.env.example` (placeholders) is committed.
- The app connects to MySQL as `resumeiq`, never as `root`.
- Only `VITE_`-prefixed variables reach the browser bundle — that prefix is a
  security boundary. Google's client **secret** must never live in `frontend/`.
- Every protected endpoint will enforce row-level ownership, not just
  authentication: user A must never read user B's analyses.
