import io
import os
import tempfile
from unittest.mock import patch, MagicMock
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


def test_import_downloads_remote_images(client: TestClient, admin_token, session):
    """Remote image URLs in markdown are downloaded and rewritten to local paths."""
    from app.models import Article
    from sqlmodel import select

    markdown = b"""---
title: Article With Image
---

# Hello

![Alt text](https://example.com/image.png)

Some text after.
"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "image/png"}
    mock_response.content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # PNG header

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("app.services.markdown_import_service.httpx.get", return_value=mock_response):
            with patch("app.services.markdown_import_service.storage") as mock_storage:
                mock_storage.save.return_value = {
                    "storage_path": "2026/05/abc123_image.png",
                    "url": "/uploads/2026/05/abc123_image.png",
                    "size_bytes": 108,
                }

                files = [("files", ("article-with-image.md", markdown, "text/markdown"))]
                response = client.post(
                    "/api/admin/articles/import",
                    files=files,
                    headers=admin_token,
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data["successes"]) == 1
                assert len(data["errors"]) == 0

                # Verify image URL was rewritten
                article = session.exec(select(Article).where(Article.slug == "article-with-image")).first()
                assert article is not None
                content = article.content
                image_node = _find_image_node(content)
                assert image_node is not None
                assert image_node["attrs"]["src"] == "/uploads/2026/05/abc123_image.png"

                # Verify storage.save was called
                mock_storage.save.assert_called_once()
                call_args = mock_storage.save.call_args
                assert call_args[1]["mime_type"] == "image/png"


def test_import_keeps_local_urls_unchanged(client: TestClient, admin_token, session):
    """Already-local URLs (starting with /uploads/) are left unchanged."""
    from app.models import Article
    from sqlmodel import select

    markdown = b"""---
title: Article With Local Image
---

# Hello

![Local image](/uploads/2025/01/existing.png)

Some text.
"""

    with patch("app.services.markdown_import_service.httpx.get") as mock_get:
        files = [("files", ("local-image.md", markdown, "text/markdown"))]
        response = client.post(
            "/api/admin/articles/import",
            files=files,
            headers=admin_token,
        )
        assert response.status_code == 200

        article = session.exec(select(Article).where(Article.slug == "article-with-local-image")).first()
        assert article is not None
        image_node = _find_image_node(article.content)
        assert image_node is not None
        assert image_node["attrs"]["src"] == "/uploads/2025/01/existing.png"

        # httpx.get should NOT be called for local URLs
        mock_get.assert_not_called()


def test_import_download_failure_keeps_original_url(client: TestClient, admin_token, session):
    """When image download fails, original remote URL is preserved."""
    from app.models import Article
    from sqlmodel import select

    markdown = b"""---
title: Article With Broken Image
---

# Hello

![Broken image](https://example.com/missing.jpg)

Some text.
"""

    with patch("app.services.markdown_import_service.httpx.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")

        files = [("files", ("broken-image.md", markdown, "text/markdown"))]
        response = client.post(
            "/api/admin/articles/import",
            files=files,
            headers=admin_token,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["successes"]) == 1
        # Error logged but article still imported
        assert data["errors"][0]["filename"] == "broken-image.md"
        assert "image" in data["errors"][0]["error"].lower()

        article = session.exec(select(Article).where(Article.slug == "article-with-broken-image")).first()
        assert article is not None
        image_node = _find_image_node(article.content)
        assert image_node is not None
        # Original URL preserved
        assert image_node["attrs"]["src"] == "https://example.com/missing.jpg"


def test_import_rejects_invalid_mime_type(client: TestClient, admin_token, session):
    """Images with non-allowed MIME types are not downloaded, original URL kept."""
    from app.models import Article
    from sqlmodel import select

    markdown = b"""---
title: Article With Svg Image
---

# Hello

![SVG image](https://example.com/icon.svg)

Some text.
"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "image/svg+xml"}
    mock_response.content = b"<svg></svg>"

    with patch("app.services.markdown_import_service.httpx.get", return_value=mock_response):
        files = [("files", ("svg-image.md", markdown, "text/markdown"))]
        response = client.post(
            "/api/admin/articles/import",
            files=files,
            headers=admin_token,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["successes"]) == 1

        article = session.exec(select(Article).where(Article.slug == "article-with-svg-image")).first()
        assert article is not None
        image_node = _find_image_node(article.content)
        assert image_node is not None
        # Original URL kept since SVG is not in ALLOWED_IMAGE_TYPES
        assert image_node["attrs"]["src"] == "https://example.com/icon.svg"


def _find_image_node(tiptap_doc: dict) -> dict | None:
    """Recursively search TipTap JSON for an image node."""
    if tiptap_doc.get("type") == "image":
        return tiptap_doc
    if "content" in tiptap_doc:
        for child in tiptap_doc["content"]:
            result = _find_image_node(child)
            if result:
                return result
    return None
