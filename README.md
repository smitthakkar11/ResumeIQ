# ResumeIQ

Transparent resume ↔ job description compatibility analysis, built with classical
NLP — TF-IDF, cosine similarity and explicit skill matching. **No LLM, no external
AI API.** Every number in the final score can be traced back to the source text.

> **Status:** Phase 7 of 10 complete (User history & versioning).

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
| Frontend | React 19, Vite, JavaScript, Tailwind CSS v4, React Router, Axios, Recharts |
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
cd frontend && npm run build && npm run lint
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
| `POST` | `/api/analyses` | Bearer | score a resume against a job description, and save it |
| `GET` | `/api/analyses` | Bearer | your history, newest first |
| `GET` | `/api/analyses/{id}` | Bearer | one saved analysis |
| `DELETE` | `/api/analyses/{id}` | Bearer | delete an analysis |
| `GET` | `/api/jobs` | Bearer | job descriptions you have analysed against |
| `GET` | `/api/jobs/{id}` | Bearer | one job description |

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

### History and persistence

Analyses are stored as **immutable snapshots**, not recomputed on read. The
skill dictionary and the scoring weights change over time; if we recomputed, an
analysis you ran in August would silently show a different score in September.
This is deliberate denormalisation — the data is derivable in principle, but
the derivation is not stable.

`matched_skills`, `keywords`, `sections` and `recommendations` are MySQL `JSON`
columns rather than four more tables, because we only ever read them back whole
to render one page. The rule: **normalise what you query, serialise what you
only display.** If "find every analysis where Docker was missing" ever becomes
a requirement, that is the moment to normalise.

**Deleting a resume does not delete its analyses.** The foreign key is
`ON DELETE SET NULL`, and `resume_filename` is stored on the analysis row, so
history stays readable rather than developing holes. `user_id` keeps
`ON DELETE CASCADE` — deleting an account should genuinely erase everything.

The history query is always "my analyses, newest first", so there is a
composite index on `(user_id, created_at)`: one index serves both the filter
and the sort, with no filesort.

Analysing the same posting against three resume versions reuses one
`job_descriptions` row, matched on a **SHA-256 of the content** (a `LONGTEXT`
column cannot be usefully indexed for equality).

Resumes get a per-user `version` number on upload — v1, v2, v3 — so the UI can
label them without asking the user to name anything.

> **Not implemented:** `POST /api/jobs` from the original spec. Job descriptions
> are created as part of running an analysis, so a second creation path would
> add a way to make rows that nothing reads.

### Resume structure

Extracted PDF text has no structure, so sections are detected heuristically: a
section is present if a **short, heading-like line** (≤60 chars) matches its
vocabulary. Contact is the exception — it is found by content (email, phone,
LinkedIn/GitHub URL), because nobody writes "CONTACT" above their own address.

Results are always phrased **"not detected"**, never "missing". A two-column
layout, a heading rendered as an image, or a creative heading ("Where I've
Worked") will all defeat it, and telling someone their resume has no experience
section when it plainly does would be worse than saying nothing.

### Recommendations

Rule-based, in
[`recommendations.py`](backend/app/services/analysis/recommendations.py). Every
message traces to a readable condition — missing skills, keyword match below
50%, no digits anywhere in the text, the phrase "responsible for", an expected
section not detected, resume length outside 200–1000 words.

**No LLM**, for three reasons: the advice is deterministic (same resume, same
advice), it is unit-testable, and it cannot hallucinate a skill the candidate
does not have. The cost is a generic tone, which is an acceptable trade for a
system whose selling point is that every output is traceable.

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
| 6 | Results dashboard + charts | ✅ Done |
| 7 | User history + resume versioning | ✅ Done |
| 8 | *Optional* supervised classifier — only with a real dataset | ⬜ |
| 9 | *Optional* local sentence-transformer semantic similarity | ⬜ |
| 10 | Testing, security, Docker, deployment | ⬜ |

---

## Frontend notes

Plain JavaScript, no TypeScript build step — `npm run build` is just
`vite build`.

Because there are no compile-time types, the shapes the backend returns are
documented as **JSDoc typedefs** at the top of
[`src/lib/api.js`](frontend/src/lib/api.js). Editors read these for
autocomplete, and they keep the frontend's expectations written down next to
the calls that rely on them — useful because nothing else now checks that the
frontend and the Pydantic schemas agree.

The practical consequence: renaming a field on the backend will not fail the
build. It will render `undefined` in the browser instead. When you change an
API response shape, grep the frontend for the old field name.

## Security notes

- `.env` files are gitignored; only `.env.example` (placeholders) is committed.
- The app connects to MySQL as `resumeiq`, never as `root`.
- Only `VITE_`-prefixed variables reach the browser bundle — that prefix is a
  security boundary. Google's client **secret** must never live in `frontend/`.
- Every protected endpoint will enforce row-level ownership, not just
  authentication: user A must never read user B's analyses.
