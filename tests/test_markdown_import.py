import io
from fastapi.testclient import TestClient


def test_import_markdown_unauthorized(client: TestClient):
    """POST /api/admin/articles/import returns 401 without auth."""
    files = [("files", ("test.md", b"# Hello\n\nWorld", "text/markdown"))]
    response = client.post("/api/admin/articles/import", files=files)
    assert response.status_code == 401


def test_import_single_markdown_file(client: TestClient, admin_token, session):
    """POST /api/admin/articles/import creates a draft article from a markdown file."""
    markdown = b"""---
title: My Test Article
tags: tech, python
---

# Hello World

This is a **test** article.

## Section Two

- Item one
- Item two
"""
    files = [("files", ("my-test-article.md", markdown, "text/markdown"))]
    response = client.post(
        "/api/admin/articles/import",
        files=files,
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["successes"]) == 1
    assert len(data["errors"]) == 0
    assert data["successes"][0]["title"] == "My Test Article"
    assert data["successes"][0]["slug"] == "my-test-article"

    # Verify article was created as draft
    from app.models import Article
    from sqlmodel import select
    article = session.exec(select(Article).where(Article.slug == "my-test-article")).first()
    assert article is not None
    assert article.status == "draft"
    assert article.title == "My Test Article"
    assert len(article.tags) == 2
    tag_names = {t.name for t in article.tags}
    assert tag_names == {"tech", "python"}
    # Verify content is TipTap JSON
    assert article.content["type"] == "doc"


def test_import_slug_conflict_auto_resolve(client: TestClient, admin_token, session):
    """Importing a file with a duplicate slug appends a counter."""
    from app.models import Article
    from app.services.article_service import create_article
    from sqlmodel import select

    # Create an existing article with the same slug
    create_article(session, "My Test Article", {"type": "doc", "content": []}, send_newsletter=False)
    session.commit()

    markdown = b"""---
title: My Test Article
---

# Duplicate Title
"""
    files = [("files", ("my-test-article.md", markdown, "text/markdown"))]
    response = client.post(
        "/api/admin/articles/import",
        files=files,
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["successes"]) == 1
    assert data["successes"][0]["slug"] == "my-test-article-2"

    # Verify both articles exist
    articles = session.exec(select(Article).where(Article.title == "My Test Article")).all()
    assert len(articles) == 2
    slugs = {a.slug for a in articles}
    assert slugs == {"my-test-article", "my-test-article-2"}


def test_import_missing_title_falls_back_to_filename(client: TestClient, admin_token, session):
    """When frontmatter has no title, filename is used as fallback."""
    from app.models import Article
    from sqlmodel import select

    markdown = b"""---
tags: test
---

# Some Content
"""
    files = [("files", ("awesome-post.md", markdown, "text/markdown"))]
    response = client.post(
        "/api/admin/articles/import",
        files=files,
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["successes"][0]["title"] == "Awesome Post"
    assert data["successes"][0]["slug"] == "awesome-post"

    article = session.exec(select(Article).where(Article.slug == "awesome-post")).first()
    assert article is not None
    assert article.title == "Awesome Post"


def test_import_multiple_files_mixed_results(client: TestClient, admin_token, session):
    """Importing multiple files reports successes and errors separately."""
    from app.models import Article
    from sqlmodel import select

    valid_md = b"""---
title: Valid Article
---

# Hello
"""
    non_utf8 = b"\x80\x81\x82\x83\xff\xfe"

    files = [
        ("files", ("valid.md", valid_md, "text/markdown")),
        ("files", ("binary.dat", non_utf8, "application/octet-stream")),
    ]
    response = client.post(
        "/api/admin/articles/import",
        files=files,
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["successes"]) == 1
    assert len(data["errors"]) == 1
    assert data["successes"][0]["title"] == "Valid Article"
    assert data["errors"][0]["filename"] == "binary.dat"
    assert "utf-8" in data["errors"][0]["error"].lower()

    # Verify only the valid article was created
    articles = session.exec(select(Article)).all()
    assert len(articles) == 1
    assert articles[0].title == "Valid Article"
