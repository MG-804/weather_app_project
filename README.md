# Full-Stack Weather Dashboard

A full-stack weather tracking application built with **React (Vite)** and **Flask**, featuring JWT authentication, Pydantic request validation, and live 5-day weather forecasts via the OpenWeatherMap API.

---

## Key Features & Architecture

- **Web-Token Authentication:**
- **Schema-Based Backend Validation:** Input payloads for registration and login are validated with **Pydantic**.
- **Personalized Weather List:** Authenticated users can search cities, add them to their personal dashboard, view current weather conditions + 5-day temperature trends, and remove cities.
- **Protected Client Routing:** Custom route guards manage redirects based on session state.

---

## Tech Stack

- **Frontend:** React, React Context API, React Router, FontAwesome, Vite
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Bcrypt, Flask-CORS, Flask-APScheduler, Pydantic
- **External API:** OpenWeatherMap API

---

## Local Setup & Installation

### 1. Backend Setup (`backend/`)

```bash
cd backend
python -m venv venv

# Activate virtual environment:
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Fill in your SECRET_KEY, JWT_SECRET_KEY, and WEATHER_API_KEY inside .env

python app.py
```

### 2. Frontend Setup (`frontend/`)

```bash
cd frontend
npm install
cp .env.example .env

npm run dev
```

Open `http://localhost:5173` in your browser.
