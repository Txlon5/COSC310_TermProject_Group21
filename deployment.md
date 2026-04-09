# Project - Deployment Guide

> **COSC 310 - Term Project, Group 21**
> Food delivery platform built with FastAPI (Python) + React (Vite), deployed via Docker Compose.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Requirements](#2-requirements)
3. [Setup &amp; Deployment](#3-setup--deployment)
4. [Environment Variables](#4-environment-variables)
5. [Email Setup](#5-email-setup)
6. [Test Accounts](#6-test-accounts)
7. [Running Tests](#7-running-tests)
8. [Local Development](#8-local-development)
9. [Data Storage](#9-data-storage)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Overview

```
COSC310_TermProject_Group21/
├── backend/                  # FastAPI Python API
│   ├── app/
│   │   ├── main.py
│   │   ├── .env              # Your config (SMTP, Site URL)
│   │   ├── .env_example      # Template — copy this first
│   │   ├── auth/
│   │   ├── data/             # JSON file storage
│   │   ├── routers/
│   │   ├── schemas/
│   │   └── services/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # React + Vite
│   ├── src/
│   ├── nginx.conf
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── rebuild.sh
```

Once running, the app is available at:

| Service      | URL                                |
| ------------ | ---------------------------------- |
| Production   | https://platter.quietrecords.store |
| Frontend     | http://localhost:3000              |
| Backend API  | http://localhost:8000              |
| Swagger Docs | http://localhost:8000/docs         |

---

## 2. Requirements

You need **Docker** (v24+) and **Git** installed — that's it. Docker Desktop on Mac/Windows includes everything you need. On Linux, also install the `docker-compose-plugin` package.

- Docker: https://docs.docker.com/get-docker/
- Git: https://git-scm.com/

---

## 3. Setup & Deployment

**1. Clone the repo**

```bash
git clone <repository-url>
cd COSC310_TermProject_Group21
```

**2. Set up your environment file**

```bash
cp backend/app/.env_example backend/app/.env
```

Then open `backend/app/.env` and fill in your SMTP credentials (see [Email Setup](#5-email-setup)). Everything else can stay as-is for local use.

**3. Start the app**

```bash
docker compose up --build -d
```

The first build takes 2–5 minutes. After that, it's much faster.

**4. To wipe all data and start fresh**

```bash
docker compose down -v && docker compose up --build -d
```

### Other Commands

```bash
docker compose logs -f           # Live logs (all services)
docker compose logs -f backend   # Backend logs only
docker compose down              # Stop everything
git pull && docker compose up --build -d  # Update the app
```

---

## 4. Environment Variables

All config lives in `backend/app/.env`.

| Variable         | Description                                    | Example                   |
| ---------------- | ---------------------------------------------- | ------------------------- |
| `SMTP_HOST`    | Your SMTP server                               | `smtp.gmail.com`        |
| `SMTP_PORT`    | SMTP port (587 for STARTTLS)                   | `587`                   |
| `SMTP_USER`    | SMTP login email                               | `you@gmail.com`         |
| `SMTP_PASS`    | SMTP password or app password                  | `your-app-password`     |
| `FROM_EMAIL`   | The "from" address on outgoing emails          | `you@gmail.com`         |
| `FRONTEND_URL` | Base URL of the frontend (used in email links) | `http://localhost:3000` |

> If `FRONTEND_URL` is wrong, links in verification and password reset emails will be broken.

After editing `.env`, rebuild the backend:

```bash
docker compose up --build backend -d
```

---

## 5. Email Setup

The app sends emails for **account verification** and **password resets** via SMTP (port 587, STARTTLS).

### Gmail

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=you@gmail.com
```

> Gmail requires 2FA + an [App Password](https://myaccount.google.com/apppasswords). Use that as `SMTP_PASS`.

---

## 6. Test Accounts

These accounts are preloaded and ready to use:

| Name       | Email                  | Password         | Role  |
| ---------- | ---------------------- | ---------------- | ----- |
| Jane Doe   | jane.doe@example.com   | `Password123!` | User  |
| John Smith | john.smith@example.com | `Password123!` | Admin |

---

## 7. Running Tests

Run tests directly against the backend.

```bash
cd backend
pip install -r requirements.txt   # First time only
pytest                            # Run all tests in backend/test folder
coverage run -m pytest		  # With coverage
coverage report			  # View coverage results
```

---

## 8. Local Development

If you'd rather run without Docker:

**Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
fastapi dev app/main.py          # Runs on :8000 with quick reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev                      # Runs on :3000, proxies /api → :8000
```

Both need to be running at the same time.

---

## 9. Data Storage

All application data is persisted as JSON files in `backend/app/data/`. These files store users, orders, restaurants, menus, carts, payment methods, transactions, tokens, and notifications.

---

## 10. Troubleshooting

| Problem                  | Likely Cause              | Fix                                               |
| ------------------------ | ------------------------- | ------------------------------------------------- |
| Emails not arriving      | Wrong SMTP credentials    | Double-check `backend/app/.env`                 |
| Email links are broken   | `FRONTEND_URL` is wrong | Update `FRONTEND_URL` in `.env`, then rebuild |
| Frontend 502 Bad Gateway | Backend isn't running     | Run `docker compose logs backend`               |
| Port 3000 already in use | Another process           | Change `"3000:80"` in `docker-compose.yml`    |
