# Fullstack App

This repository contains a small full-stack example with a static frontend and a minimal Python backend. It also contains optional monitoring configuration for Prometheus.

Project layout
- `backend/` - Python backend (Flask) with `app.py` and `requirements.txt`.
- `frontend/` - Static site pages and styles (`index.html`, `about.html`, `contact.html`, `services.html`, `portfolio.html`, `style.css`).
- `prometheus/` - Prometheus configuration (`prometheus.yml`) (restored).
- `docker-compose.yml` - development container composition.
- `tools/` - helper scripts (contrast check helpers).

Quick start (local)
1. Backend: create a Python virtual environment and install dependencies:

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt

2. Run backend:

   python backend/app.py

3. Open the frontend pages by opening `frontend/index.html` in your browser, or run the frontend via a static file server.

Notes
- The repository uses CSS custom properties for theming in `frontend/style.css`.
- Prometheus configuration was restored to `prometheus/prometheus.yml`.
- If you want changes pushed to the remote branch, run `git push origin staging`.

If you need this README expanded (usage, endpoints, env vars), tell me what details to add.
