# Movie Platform — Starter

Render-ready foundation for a movie website.

## Structure
- `frontend/` — React + Vite mobile-first UI
- `backend/` — FastAPI API
- MongoDB and movie storage are intentionally separated so storage can be changed later.

## Local run
Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Render
Deploy backend as a Web Service using:
`pip install -r requirements.txt`
Start:
`uvicorn main:app --host 0.0.0.0 --port $PORT`

Deploy frontend as a Static Site using:
`npm install && npm run build`
Publish directory:
`dist`

Set `VITE_API_URL` on the frontend to the deployed backend URL.
