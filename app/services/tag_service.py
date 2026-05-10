import uuid
import re
from typing import List
from sqlmodel import Session, select
from app.models.tag import Tag

def generate_tag_slug(name: str, session: Session) -> str:
    """Generate a unique URL slug from a tag name."""
    base = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not base:
        base = "tag"
    
    slug = base
    counter = 2
    while session.exec(select(Tag).where(Tag.slug == slug)).first():
        slug = f"{base}-{counter}"
        counter += 1
    
    return slug

def get_or_create_tags(session: Session, names: List[str]) -> List[Tag]:
    """Get existing tags by name (case-insensitive) or create new ones."""
    if not names:
        return []
    
    tags = []
    for name in names:
        name = name.strip()
        if not name:
            continue
        
        # Case-insensitive lookup
        existing = session.exec(
            select(Tag).where(Tag.name.ilike(name))
        ).first()
        
        if existing:
            tags.append(existing)
        else:
            slug = generate_tag_slug(name, session)
            tag = Tag(name=name, slug=slug)
            session.add(tag)
            session.commit()
            session.refresh(tag)
            tags.append(tag)
    
    return tags
