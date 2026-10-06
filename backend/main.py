from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Movie Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Movie(BaseModel):
    title: str
    description: str = ""
    poster_url: str = ""
    backdrop_url: str = ""
    category: str = "Movies"
    year: Optional[int] = None
    duration: Optional[str] = None
    video_url: str = ""

DEMO_MOVIES = [
    Movie(
        title="Featured Movie",
        description="Add your first movie from the admin panel.",
        poster_url="https://placehold.co/600x900/171126/ffffff?text=Movie",
        backdrop_url="https://placehold.co/1600x700/171126/ffffff?text=Featured+Movie",
        category="Featured",
        year=2026,
        duration="2h 00m",
    )
]

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "movie-platform"}

@app.get("/api/movies")
def movies():
    return {"items": [m.model_dump() for m in DEMO_MOVIES]}

@app.get("/api/movies/{index}")
def movie(index: int):
    if index < 0 or index >= len(DEMO_MOVIES):
        return {"error": "Movie not found"}
    return DEMO_MOVIES[index].model_dump()
