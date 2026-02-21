# LoC ANTI — AI-Powered Local Labour Platform

A monorepo connecting **clients** with local **skilled workers**, powered by Gemini AI, real-time WebSockets, and voice-first UI.

## 🏗️ Architecture

```
loc ANTI/
├── backend/              # FastAPI + PostgreSQL (port 8000)
├── frontend-worker/      # React/Vite — Worker App (port 3000)
├── frontend-client/      # React/Vite — Client App (port 4000)
├── docker-compose.yml
├── .env                  # ← Add your GEMINI_API_KEY here!
└── .env.example
```

## 🚀 Quick Start

### 1. Set your Gemini API Key
```bash
# Edit .env and replace the placeholder:
GEMINI_API_KEY=your_actual_key_here
```

### 2. Launch everything with Docker Compose
```bash
cd "loc ANTI"
docker-compose up --build
```

| Service | URL |
|---------|-----|
| Backend API (Swagger) | http://localhost:8000/docs |
| Worker App | http://localhost:3000 |
| Client App | http://localhost:4000 |
| PostgreSQL | localhost:5432 |

---

## ✨ Features

### Backend (FastAPI)
- **`POST /ai/analyze-problem`** — Upload image → Gemini Flash returns `{summary, severity, parts_list, estimated_cost_inr}`
- **WebSocket `/ws/{worker_id}`** — Real-time "Deal Done" push notifications
- **Translation Middleware** — `X-User-Language: hi/mr/te` header auto-translates job descriptions via Gemini
- **Full CRUD**: Jobs, Bids, Users, Reviews, WorkHistory
- **`POST /deals/accept`** — Marks bid, updates job, fires WebSocket to worker

### Worker App (Port 3000)
- 🌍 **4-language support**: English, Hindi (हिंदी), Marathi (मराठी), Telugu (తెలుగు)
- 🔊 **TTS Listen button** — Web Speech API reads job summaries aloud
- 🎤 **Voice Bidding** — Say your price, STT extracts the integer and auto-fills the form
- 💰 **Earnings Wallet** — Monthly bar chart + stats for total earnings & jobs completed
- 🔔 **Deal Done popup** — WebSocket notification with auto-reconnect

### Client App (Port 4000)
- 📷 **Smart Job Posting** — Image upload triggers instant Gemini AI diagnostic
- 📊 **Bid Comparison Engine** — Sortable table with worker avg rating, total jobs, and bid amount
- 🤝 **Accept Handshake** — Accept button notifies the worker in real-time via WebSocket

---

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key (required) |
| `POSTGRES_USER` | DB username (default: `locuser`) |
| `POSTGRES_PASSWORD` | DB password (default: `locpassword`) |
| `POSTGRES_DB` | DB name (default: `locdb`) |

---

## 🗄️ Database Models

- **User** — client or worker, with preferred_language
- **Job** — with `ai_summary` JSON column (from Gemini)
- **Bid** — worker bids on jobs with amount + message
- **Review** — rating (1–5) per completed job
- **WorkHistory** — tracks earnings per completed job

---

## 📡 API Quick Reference

```
GET    /jobs                     List jobs (filter: status, client_id)
POST   /jobs                     Create job
GET    /jobs/{id}                Get job by ID
POST   /ai/analyze-problem       Gemini image analysis
POST   /bids                     Place a bid
GET    /bids?job_id=&worker_id=  Filter bids
GET    /bids/worker/{id}/stats   Worker stats (jobs done, earnings)
POST   /reviews                  Submit review
GET    /reviews/worker/{id}/stats  Avg rating
POST   /deals/accept             Accept bid → WebSocket notification
WS     /ws/{worker_id}           Worker WebSocket connection
```
