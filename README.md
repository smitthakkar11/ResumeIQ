# ResumeIQ

Transparent resume ↔ job description compatibility analysis, built with classical
NLP — TF-IDF, cosine similarity and explicit skill matching. **No LLM, no external
AI API.** Every number in the final score can be traced back to the source text.

> **Status:** Phase 2 of 10 complete (Authentication).

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

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/` | — | service metadata |
| `GET` | `/api/health` | — | liveness — is the process up? |
| `GET` | `/api/health/db` | — | readiness — can it reach MySQL? |
| `POST` | `/api/auth/signup` | — | register, returns an access token |
| `POST` | `/api/auth/login` | — | exchange credentials for a token |
| `POST` | `/api/auth/google` | — | exchange a Google auth code for a token |
| `GET` | `/api/auth/me` | Bearer | the authenticated user |
| `GET` | `/api/auth/providers` | — | which sign-in methods are configured |

Resume, job and analysis endpoints arrive in Phases 3–5.

### Authentication

Passwords are hashed with **bcrypt** at cost 12 (2¹² rounds, ~200 ms per hash)
with a per-password random salt. Sessions use **JWTs** signed with HS256 and a
60-minute expiry — short because a JWT cannot be revoked once issued.

Login failures return one message (`Incorrect email or password`) whether the
email is unknown or the password is wrong, so the endpoint cannot be used to
enumerate registered accounts.

### Google Sign-In (optional)

Uses the OAuth 2.0 **authorization code flow**. The browser receives a one-time
code; the backend redeems it with `GOOGLE_CLIENT_SECRET`, verifies the returned
`id_token` against Google's public keys (checking signature, `aud` and `iss`),
then issues one of our own JWTs. The client secret never reaches the browser.

To enable it:

1. In [Google Cloud Console](https://console.cloud.google.com/apis/credentials),
   create an **OAuth client ID** of type *Web application*.
2. Add `http://localhost:5174/login` as an **Authorized redirect URI**.
3. Put the client ID and secret in `backend/.env`.

Leave those variables blank and the app runs normally — the Google button
simply does not render, and `POST /api/auth/google` returns 503.

---

## Roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Foundation: React + FastAPI + MySQL + Alembic | ✅ Done |
| 2 | Auth: JWT, password hashing, Google Sign-In | ✅ Done |
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
