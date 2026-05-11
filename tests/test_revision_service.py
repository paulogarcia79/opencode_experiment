from datetime import datetime, timezone
from app.models.article import Article
from app.models.article_revision import ArticleRevision
from app.services.article_service import create_article, update_article
from app.services.revision_service import (
    create_revision,
    list_revisions,
    get_revision,
    _next_version_number,
)


def test_next_version_number_starts_at_one(session):
    article = create_article(session, "Test", {"type": "doc"})
    assert _next_version_number(session, article.id) == 1


def test_next_version_number_increments(session):
    article = create_article(session, "Test", {"type": "doc"})
    create_revision(session, article, "save")
    assert _next_version_number(session, article.id) == 2


def test_next_version_number_scoped_per_article(session):
    article_a = create_article(session, "Article A", {"type": "doc"})
    article_b = create_article(session, "Article B", {"type": "doc"})
    create_revision(session, article_a, "save")
    create_revision(session, article_a, "save")
    assert _next_version_number(session, article_a.id) == 3
    assert _next_version_number(session, article_b.id) == 1


def test_create_revision_captures_snapshot(session):
    article = create_article(
        session,
        "Original Title",
        {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}]},
        description="Original description",
        tag_names=["tech", "python"],
    )
    revision = create_revision(session, article, "save")
    assert revision.article_id == article.id
    assert revision.version_number == 1
    assert revision.title == "Original Title"
    assert revision.content["type"] == "doc"
    assert revision.description == "Original description"
    assert set(revision.tag_names) == {"tech", "python"}
    assert revision.change_type == "save"
    assert revision.created_at is not None


def test_create_revision_assigns_sequential_versions(session):
    article = create_article(session, "Test", {"type": "doc"})
    r1 = create_revision(session, article, "save")
    r2 = create_revision(session, article, "save")
    r3 = create_revision(session, article, "publish")
    assert r1.version_number == 1
    assert r2.version_number == 2
    assert r3.version_number == 3
    assert r3.change_type == "publish"


def test_list_revisions_returns_newest_first(session):
    article = create_article(session, "Test", {"type": "doc"})
    create_revision(session, article, "save")
    create_revision(session, article, "save")
    create_revision(session, article, "publish")
    revisions = list_revisions(session, article.id)
    assert len(revisions) == 3
    assert revisions[0].version_number == 3
    assert revisions[1].version_number == 2
    assert revisions[2].version_number == 1


def test_list_revisions_empty_for_article_without_revisions(session):
    article = create_article(session, "Test", {"type": "doc"})
    revisions = list_revisions(session, article.id)
    assert revisions == []


def test_get_revision_returns_full_data(session):
    article = create_article(
        session,
        "Title",
        {"type": "doc"},
        description="Desc",
        tag_names=["tag1"],
    )
    create_revision(session, article, "save")
    revision = get_revision(session, article.id, 1)
    assert revision is not None
    assert revision.title == "Title"
    assert revision.description == "Desc"
    assert set(revision.tag_names) == {"tag1"}


def test_get_revision_returns_none_for_missing_version(session):
    article = create_article(session, "Test", {"type": "doc"})
    revision = get_revision(session, article.id, 999)
    assert revision is None


def test_get_revision_returns_none_for_missing_article(session):
    import uuid
    revision = get_revision(session, uuid.uuid4(), 1)
    assert revision is None


def test_create_revision_after_update_captures_updated_state(session):
    article = create_article(session, "Original", {"type": "doc"}, description="Old desc")
    create_revision(session, article, "save")
    update_article(session, article, title="Updated", description="New desc")
    r2 = create_revision(session, article, "save")
    assert r2.title == "Updated"
    assert r2.description == "New desc"
    assert r2.version_number == 2
