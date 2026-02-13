from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.cache.db import init_db
from app.db.events_queries import init_events_db
from app.routers.auth_router import router as auth_router
from app.routers.iracing_router import router as iracing_router
from app.routers.events_router import router as events_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()
init_events_db()

app.include_router(auth_router)
app.include_router(iracing_router)
app.include_router(events_router)
