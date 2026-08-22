# ResumeIQ

Transparent resume ↔ job description compatibility analysis, built with classical
NLP — TF-IDF, cosine similarity and explicit skill matching. **No LLM, no external
AI API.** Every number in the final score can be traced back to the source text.

> **Status:** Phase 5 of 10 complete (Matching engine).

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
| `POST` | `/api/resumes/upload` | Bearer | upload a PDF, returns extracted text |
| `GET` | `/api/resumes` | Bearer | your resumes (summaries only) |
| `GET` | `/api/resumes/{id}` | Bearer | one resume with its text |
| `GET` | `/api/resumes/{id}/skills` | Bearer | skills detected in a resume |
| `DELETE` | `/api/resumes/{id}` | Bearer | delete a resume |
| `POST` | `/api/analyses` | Bearer | score a resume against a job description |

Job and analysis endpoints arrive in Phases 4–5. Every resume endpoint filters
by `user_id` inside the query, and returns **404** (not 403) for someone else's
resume, so it never confirms that another user's data exists.

### Matching engine

```
Overall = 0.40 x Text similarity   (TF-IDF cosine)
        + 0.40 x Skill match       (matched required / total required)
        + 0.20 x Keyword match     (top job-description terms found in resume)
```

Weights are set in `.env` (`TEXT_SIMILARITY_WEIGHT`, `SKILL_MATCH_WEIGHT`,
`KEYWORD_MATCH_WEIGHT`) and must sum to 1.0. Every component is returned
separately, so a user can see which part is weak.

**Text similarity** — both documents are preprocessed, vectorised with
`TfidfVectorizer`, and compared with `cosine_similarity`. sklearn L2-normalises
each row, so both vectors have length 1 and the cosine reduces to a dot
product. Cosine is used rather than Euclidean distance because it measures the
**angle** between vectors: a two-page resume and a five-line job posting differ
enormously in magnitude but that is a length difference, not a mismatch.

**Skill match** — `matched required skills / total required skills`. Skills the
candidate has that the job never asked for are reported as "extra" but earn no
points.

**Keyword match** — the top-N terms of the job description (N configurable),
checked for presence in the resume. Job-posting boilerplate (`experience`,
`plus`, `knowledge`, `team`, `responsibility`…) is filtered out first — a
domain-specific stop list, since no resume should be penalised for lacking
those words.

**If the job description names no skills we recognise**, the skill component is
*dropped* and the remaining weights are rescaled, rather than scored as 0.
We did not measure it; reporting 0 would be misleading.

#### Honest limitations

- **No semantics.** "ML" and "machine learning" are different dimensions.
- **No word order.** It is a bag of words.
- **IDF is weak with two documents.** With n=2, `df` is only ever 1 or 2, so
  idf takes just two values and terms shared by both documents get the *lower*
  weight. Real IDF needs a corpus of job descriptions. Consequently raw text
  similarity runs low (often 10–40%) and is most meaningful **comparatively** —
  resume A vs resume B for the same job — rather than as an absolute number.
- **Keyword stuffing defeats it**, as it defeats any purely lexical method.

### NLP preprocessing

Two paths run from the same extracted text, and keeping them separate is the
key design decision:

```
extracted text
   ├─► light normalise ──► skill extraction   (exact alias matching)
   └─► full preprocess  ──► TF-IDF / keywords (Phase 5)
```

If we lemmatised and stripped punctuation before looking for skills, `C++`
would already be gone. The tokenizer therefore treats `+ # . -` as
word-**internal** characters — a plain `\w+` turns `C++` into `c`, `.NET` into
`net` and `Node.js` into two tokens.

Full pipeline: normalise → tokenize → drop stop words → **lemmatize**
(spaCy `en_core_web_sm`, parser and NER disabled). Lemmatization over stemming
because it returns real words — `studies → study`, not `studi` — and can use
part of speech, so `better → well`.

### Skill extraction

A curated dictionary in
[`skills.json`](backend/app/services/nlp/skills.json) (84 skills), edited as
data rather than code. Each entry has a canonical name plus aliases, so
`reactjs`, `react.js` and `react js` all resolve to **React**.

Aliases that are ordinary English words are deliberately excluded — `rest`,
`spring`, `express`, `node`, `spark` — and `Go` matches only `golang`, never
the bare word. That trades a few false negatives for avoiding absurd false
positives like "the rest of the team".

**Limitation:** a dictionary only finds skills it already knows. That is the
price of being able to explain every match.

### PDF extraction

A PDF stores positioned glyphs, not text — extraction reassembles them, and
multi-column layouts, tables and ligatures all distort the result. We accept
that noise deliberately and keep the extracted text visible in the UI so you
can see exactly what the matching engine will read.

Uploads are validated in cost order: size (5 MB), then magic bytes (`%PDF-` —
never the filename or `Content-Type`, which the client controls), then parsing.
Encrypted, corrupt, zero-page and over-20-page files all return 400.

Scanned resumes contain no text layer, so extraction yields nothing. Rather
than analysing an empty string, we detect it and say so. OCR is out of scope.

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
| 3 | Resume upload + PDF text extraction | ✅ Done |
| 4 | NLP: preprocessing, skill dictionary, extraction | ✅ Done |
| 5 | Matching engine: TF-IDF, cosine similarity, scoring | ✅ Done |
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
