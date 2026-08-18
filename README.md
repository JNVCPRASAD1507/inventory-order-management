# Inventory & Order Management System — Full Stack (Production Ready)

React + Material UI + Recharts frontend · FastAPI + SQLAlchemy + PostgreSQL/SQLite backend

## Features

- JWT auth + Admin / Staff / Customer RBAC
- Products, Categories, Inventory (no negative stock)
- Orders with valid status transitions + stock restore on cancel
- Payments simulation, Reviews, Notifications (BackgroundTasks)
- Role dashboards + Daily / Weekly / Monthly charts
- Glassmorphism UI with linear gradients
- Alembic migrations + Docker Compose
- Demo seed data

## Quick start (local, no Docker)

### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
# Uses SQLite by default via backend/.env
python seed_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
UI: http://localhost:5173

## Docker (PostgreSQL production-style)

```bash
cp .env.example .env   # optional; .env already present
docker compose up --build
```

- Frontend: http://localhost:5173  
- API / Swagger: http://localhost:8000/docs  

## Demo accounts

| Role     | Email                 | Password    |
|----------|-----------------------|-------------|
| Admin    | admin@example.com     | admin123    |
| Staff    | staff@example.com     | staff123    |
| Customer | customer@example.com  | customer123 |

Instead of using dummy mails to login use the real time g-mail id to get the better experience...
dummy mails won't works 😎😎😎

create u r own admin , staff , customer account ...
The above data is for just show off 😜😜

## Production notes

1. Set a strong `SECRET_KEY` and Postgres credentials in `.env`
2. Terminate TLS at nginx / load balancer
3. Prefer `alembic upgrade head` over auto `create_all` in production
4. Store uploads on object storage (S3) if scaling

## Project layout

```
backend/app/{api,core,db,models,repositories,schemas,services,utils}
frontend/src/{api,components,context,pages,routes,theme}
docs/  postman + schema
```
