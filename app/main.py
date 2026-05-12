from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import create_db_and_tables, get_session
from app.routers import articles, subscribers, images, auth, analytics, webhooks, oauth
from app.routers.settings import router as settings_router
from app.routers.analytics import article_analytics_router
from app.models import User, Article, Subscriber, NewsletterSend, ImageAsset, Tag, ArticleTag
from app.services.seed_service import seed_default_admin
from app.limiter import limiter, rate_limit_exceeded_handler
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

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(subscribers.router)
app.include_router(images.router)
app.include_router(analytics.router)
app.include_router(article_analytics_router)
app.include_router(webhooks.router)
app.include_router(oauth.router)
app.include_router(settings_router)
