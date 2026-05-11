from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables, get_session
from app.routers import articles, subscribers, images, auth, analytics, webhooks
from app.models import User, Article, Subscriber, NewsletterSend, ImageAsset, Tag, ArticleTag
from app.services.seed_service import seed_default_admin
from arq import create_pool
from app.redis import get_redis_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    # Seed default admin if no users exist
    for session in get_session():
        seed_default_admin(session)
        break
    
    # Initialize arq pool
    app.state.arq_pool = await create_pool(get_redis_settings())
    
    yield
    
    # Shutdown
    await app.state.arq_pool.close()

app = FastAPI(title="Blog + Newsletter Platform", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(subscribers.router)
app.include_router(images.router)
app.include_router(analytics.router)
app.include_router(webhooks.router)
