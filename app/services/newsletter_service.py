from datetime import datetime
from sqlmodel import Session
from app.models.article import Article
from arq.connections import ArqRedis

async def send_newsletter_for_article(arq_pool: ArqRedis, article: Article, defer_until: datetime = None) -> None:
    """Enqueue the orchestrator job to send newsletter to all active subscribers."""
    await arq_pool.enqueue_job("blast_newsletter_task", str(article.id), _defer_until=defer_until)
