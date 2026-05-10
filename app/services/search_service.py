from typing import List
from sqlalchemy import text
from sqlmodel import Session, select
from app.models.article import Article
from app.services.content_service import extract_plain_text_from_tiptap

def build_search_text(title: str, description: str | None, content: dict, tag_names: List[str] | None = None) -> str:
    """Build searchable text from article fields."""
    parts = [title]
    if description:
        parts.append(description)
    content_text = extract_plain_text_from_tiptap(content).strip()
    if content_text:
        parts.append(content_text)
    if tag_names:
        parts.extend(tag_names)
    return " ".join(parts)

def search_articles(session: Session, query: str) -> List[Article]:
    """Search published articles by query string.
    
    Uses PostgreSQL full-text search (tsvector/tsquery) when available,
    falls back to SQLite ILIKE for test environments.
    """
    query = query.strip()
    if not query:
        return []
    
    # Check if we're on PostgreSQL by testing for tsvector support
    dialect_name = session.bind.dialect.name if session.bind else "sqlite"
    
    if dialect_name == "postgresql":
        # PostgreSQL: use full-text search with tsvector
        tsquery = " & ".join(query.split())
        sql = text("""
            SELECT * FROM articles
            WHERE status = 'published'
            AND search_text IS NOT NULL
            AND to_tsvector('english', search_text) @@ to_tsquery('english', :query)
            ORDER BY ts_rank(to_tsvector('english', search_text), to_tsquery('english', :query)) DESC
        """)
        result = session.exec(sql, params={"query": tsquery})
        return list(result)
    else:
        # SQLite fallback: use LIKE with simple relevance heuristic
        pattern = f"%{query}%"
        articles = session.exec(
            select(Article)
            .where(Article.status == "published")
            .where(Article.search_text.is_not(None))
            .where(Article.search_text.ilike(pattern))
        ).all()
        
        # Simple relevance ranking for SQLite tests:
        # title match > description match > tag match > content match
        query_lower = query.lower()
        def relevance_score(article: Article) -> int:
            score = 0
            title = (article.title or "").lower()
            desc = (article.description or "").lower()
            text = (article.search_text or "").lower()
            if query_lower in title:
                score += 100
            if query_lower in desc:
                score += 50
            # Tag match: query is in search_text but not in title or description
            if query_lower in text and query_lower not in title and query_lower not in desc:
                score += 25
            if query_lower in text:
                score += 10
            return score
        
        return sorted(articles, key=relevance_score, reverse=True)
