from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables, get_session
from app.routers import articles, subscribers, images
from app.models import User, Article, Subscriber, NewsletterSend, ImageAsset
from app.services.seed_service import seed_default_admin

app = FastAPI(title="Blog + Newsletter Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(subscribers.router)
app.include_router(images.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Seed default admin if no users exist
    for session in get_session():
        seed_default_admin(session)
        break
