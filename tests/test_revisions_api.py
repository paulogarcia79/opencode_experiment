from fastapi.testclient import TestClient
from app.services.article_service import create_article, update_article
from app.services.revision_service import create_revision
from datetime import datetime, timezone


def test_list_revisions_returns_list(client: TestClient, session, admin_token):
    article = create_article(session, "Test Article", {"type": "doc"})
    create_revision(session, article, "save")
    create_revision(session, article, "publish")

    response = client.get(
        f"/api/admin/articles/{article.id}/revisions",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["version_number"] == 2
    assert data[1]["version_number"] == 1
    assert "content" not in data[0]


def test_list_revisions_404_for_missing_article(client: TestClient, admin_token):
    import uuid
    response = client.get(
        f"/api/admin/articles/{uuid.uuid4()}/revisions",
        headers=admin_token,
    )
    assert response.status_code == 404


def test_get_revision_returns_full_data(client: TestClient, session, admin_token):
    article = create_article(
        session,
        "Original Title",
        {"type": "doc", "content": [{"type": "paragraph"}]},
        description="Original desc",
        tag_names=["tech"],
    )
    create_revision(session, article, "save")

    response = client.get(
        f"/api/admin/articles/{article.id}/revisions/1",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["version_number"] == 1
    assert data["change_type"] == "save"
    assert data["title"] == "Original Title"
    assert data["content"]["type"] == "doc"
    assert data["description"] == "Original desc"
    assert set(data["tag_names"]) == {"tech"}


def test_get_revision_404_for_missing_article(client: TestClient, admin_token):
    import uuid
    response = client.get(
        f"/api/admin/articles/{uuid.uuid4()}/revisions/1",
        headers=admin_token,
    )
    assert response.status_code == 404


def test_get_revision_404_for_missing_version(client: TestClient, session, admin_token):
    article = create_article(session, "Test", {"type": "doc"})
    response = client.get(
        f"/api/admin/articles/{article.id}/revisions/999",
        headers=admin_token,
    )
    assert response.status_code == 404


def test_list_revisions_unauthorized(client: TestClient, session):
    article = create_article(session, "Test", {"type": "doc"})
    response = client.get(f"/api/admin/articles/{article.id}/revisions")
    assert response.status_code == 401


def test_get_revision_unauthorized(client: TestClient, session):
    article = create_article(session, "Test", {"type": "doc"})
    response = client.get(f"/api/admin/articles/{article.id}/revisions/1")
    assert response.status_code == 401


def test_update_creates_revision_on_save(client: TestClient, session, admin_token):
    article = create_article(session, "Original", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"title": "Updated"},
        headers=admin_token,
    )
    assert response.status_code == 200

    revisions = client.get(
        f"/api/admin/articles/{article.id}/revisions",
        headers=admin_token,
    ).json()
    assert len(revisions) == 1
    assert revisions[0]["version_number"] == 1
    assert revisions[0]["change_type"] == "save"
    assert revisions[0]["title"] == "Original"


def test_update_creates_revision_on_publish(client: TestClient, session, admin_token):
    article = create_article(session, "Draft", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"status": "published"},
        headers=admin_token,
    )
    assert response.status_code == 200

    revisions = client.get(
        f"/api/admin/articles/{article.id}/revisions",
        headers=admin_token,
    ).json()
    assert len(revisions) == 1
    assert revisions[0]["change_type"] == "publish"


def test_autosave_does_not_create_revision(client: TestClient, session, admin_token):
    article = create_article(session, "Test", {"type": "doc"})
    response = client.put(
        f"/api/admin/articles/{article.id}/autosave",
        json={"title": "Autosaved"},
        headers=admin_token,
    )
    assert response.status_code == 200

    revisions = client.get(
        f"/api/admin/articles/{article.id}/revisions",
        headers=admin_token,
    ).json()
    assert len(revisions) == 0


def test_multiple_updates_create_multiple_revisions(client: TestClient, session, admin_token):
    article = create_article(session, "V1", {"type": "doc"})
    client.put(f"/api/articles/{article.id}", json={"title": "V2"}, headers=admin_token)
    client.put(f"/api/articles/{article.id}", json={"title": "V3"}, headers=admin_token)

    revisions = client.get(
        f"/api/admin/articles/{article.id}/revisions",
        headers=admin_token,
    ).json()
    assert len(revisions) == 2
    assert revisions[0]["version_number"] == 2
    assert revisions[1]["version_number"] == 1
    assert revisions[1]["title"] == "V1"


def test_restore_revision_reverts_content(client: TestClient, session, admin_token):
    article = create_article(session, "Original", {"type": "doc"}, description="Original desc")
    create_revision(session, article, "save")
    update_article(session, article, title="Modified", description="Modified desc")

    response = client.post(
        f"/api/admin/articles/{article.id}/revisions/1/restore",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Original"
    assert data["description"] == "Original desc"


def test_restore_revision_reverts_tags(client: TestClient, session, admin_token):
    article = create_article(session, "Test", {"type": "doc"}, tag_names=["tech", "python"])
    create_revision(session, article, "save")
    update_article(session, article, tag_names=["game-dev"])

    response = client.post(
        f"/api/admin/articles/{article.id}/revisions/1/restore",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert set(t["name"] for t in data["tags"]) == {"python", "tech"}


def test_restore_does_not_change_status(client: TestClient, session, admin_token):
    article = create_article(session, "Draft", {"type": "doc"})
    create_revision(session, article, "save")
    update_article(session, article, status="published")

    response = client.post(
        f"/api/admin/articles/{article.id}/revisions/1/restore",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "published"


def test_restore_creates_restore_revision(client: TestClient, session, admin_token):
    article = create_article(session, "V1", {"type": "doc"})
    create_revision(session, article, "save")
    client.put(f"/api/articles/{article.id}", json={"title": "V2"}, headers=admin_token)

    client.post(
        f"/api/admin/articles/{article.id}/revisions/1/restore",
        headers=admin_token,
    )

    revisions = client.get(
        f"/api/admin/articles/{article.id}/revisions",
        headers=admin_token,
    ).json()
    assert len(revisions) == 3
    assert revisions[0]["change_type"] == "restore"
    assert revisions[0]["title"] == "V1"


def test_restore_404_for_missing_article(client: TestClient, admin_token):
    import uuid
    response = client.post(
        f"/api/admin/articles/{uuid.uuid4()}/revisions/1/restore",
        headers=admin_token,
    )
    assert response.status_code == 404


def test_restore_404_for_missing_version(client: TestClient, session, admin_token):
    article = create_article(session, "Test", {"type": "doc"})
    response = client.post(
        f"/api/admin/articles/{article.id}/revisions/999/restore",
        headers=admin_token,
    )
    assert response.status_code == 404


def test_restore_unauthorized(client: TestClient, session):
    article = create_article(session, "Test", {"type": "doc"})
    response = client.post(f"/api/admin/articles/{article.id}/revisions/1/restore")
    assert response.status_code == 401


def test_restore_clears_tags_when_revision_has_none(client: TestClient, session, admin_token):
    article = create_article(session, "No Tags", {"type": "doc"})
    create_revision(session, article, "save")
    update_article(session, article, tag_names=["tech", "python"])

    response = client.post(
        f"/api/admin/articles/{article.id}/revisions/1/restore",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == []

def test_save_revision_captures_author_id(client: TestClient, session, admin_token):
    """Explicit save should capture the current user's ID in the revision."""
    from app.models.user import User
    from sqlmodel import select
    from app.models.article_revision import ArticleRevision
    
    admin = session.exec(select(User)).first()
    
    article = create_article(session, "Authored", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"title": "Updated"},
        headers=admin_token,
    )
    assert response.status_code == 200
    
    revision = session.exec(
        select(ArticleRevision).where(ArticleRevision.article_id == article.id)
    ).first()
    assert revision is not None
    assert revision.author_id == admin.id

def test_publish_revision_captures_author_id(client: TestClient, session, admin_token):
    """Publish action should capture the current user's ID in the revision."""
    from app.models.user import User
    from sqlmodel import select
    from app.models.article_revision import ArticleRevision
    
    admin = session.exec(select(User)).first()
    
    article = create_article(session, "To Publish", {"type": "doc"})
    response = client.put(
        f"/api/articles/{article.id}",
        json={"status": "published"},
        headers=admin_token,
    )
    assert response.status_code == 200
    
    revision = session.exec(
        select(ArticleRevision).where(ArticleRevision.article_id == article.id)
    ).first()
    assert revision is not None
    assert revision.author_id == admin.id

def test_autosave_does_not_capture_author_id(client: TestClient, session, admin_token):
    """Autosave should not create revisions (existing behavior preserved)."""
    from app.models.article_revision import ArticleRevision
    from sqlmodel import select
    
    article = create_article(session, "Autosave Test", {"type": "doc"})
    client.put(
        f"/api/admin/articles/{article.id}/autosave",
        json={"title": "Autosaved"},
        headers=admin_token,
    )
    
    revisions = session.exec(
        select(ArticleRevision).where(ArticleRevision.article_id == article.id)
    ).all()
    assert len(revisions) == 0

def test_revision_list_response_includes_author(client: TestClient, session, admin_token):
    """Revision list response should include author email when present."""
    from app.models.user import User
    from sqlmodel import select
    
    admin = session.exec(select(User)).first()
    
    article = create_article(session, "Revision Author Test", {"type": "doc"})
    client.put(
        f"/api/articles/{article.id}",
        json={"title": "Updated"},
        headers=admin_token,
    )
    
    response = client.get(
        f"/api/admin/articles/{article.id}/revisions",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["author_email"] == admin.email

def test_revision_read_response_includes_author(client: TestClient, session, admin_token):
    """Revision read response should include author email when present."""
    from app.models.user import User
    from sqlmodel import select
    
    admin = session.exec(select(User)).first()
    
    article = create_article(session, "Revision Read Test", {"type": "doc"})
    client.put(
        f"/api/articles/{article.id}",
        json={"title": "Updated"},
        headers=admin_token,
    )
    
    response = client.get(
        f"/api/admin/articles/{article.id}/revisions/1",
        headers=admin_token,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["author_email"] == admin.email
