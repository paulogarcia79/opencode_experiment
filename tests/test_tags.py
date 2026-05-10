import pytest
from datetime import datetime


def test_create_article_with_tags_returns_tags_in_api_response(client, session):
    """POST /api/admin/articles with tag_names should include tags in response."""
    payload = {
        "title": "Tagged Article",
        "content": {"type": "doc", "content": []},
        "description": "An article with tags",
        "tag_names": ["docker", "tutorial"],
    }
    response = client.post(
        "/api/admin/articles",
        json=payload,
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.json())
    assert response.status_code == 200
    data = response.json()
    assert "tags" in data
    assert len(data["tags"]) == 2
    tag_slugs = [t["slug"] for t in data["tags"]]
    assert "docker" in tag_slugs
    assert "tutorial" in tag_slugs


def test_tags_are_case_insensitive(client, session):
    """Creating articles with 'Docker' and 'docker' should use the same tag."""
    # First article with "Docker"
    response1 = client.post(
        "/api/admin/articles",
        json={"title": "Article 1", "content": {}, "tag_names": ["Docker"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert len(data1["tags"]) == 1
    tag_id_1 = data1["tags"][0]["slug"]

    # Second article with "docker" (lowercase)
    response2 = client.post(
        "/api/admin/articles",
        json={"title": "Article 2", "content": {}, "tag_names": ["docker"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["tags"]) == 1
    tag_id_2 = data2["tags"][0]["slug"]

    assert tag_id_1 == tag_id_2


def test_update_article_replaces_tags(client, session):
    """Updating an article with new tag_names should replace existing tags."""
    # Create article with docker tag
    create_response = client.post(
        "/api/admin/articles",
        json={"title": "Update Test", "content": {}, "tag_names": ["docker"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    article_id = create_response.json()["id"]

    # Update with vue tag
    update_response = client.put(
        f"/api/articles/{article_id}",
        json={"tag_names": ["vue"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["slug"] == "vue"


def test_tag_slugs_are_auto_generated(client, session):
    """Tag names should be converted to URL-safe slugs."""
    response = client.post(
        "/api/admin/articles",
        json={"title": "Slug Test", "content": {}, "tag_names": ["Game Design", "Vue.js"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert response.status_code == 200
    data = response.json()
    slugs = [t["slug"] for t in data["tags"]]
    assert "game-design" in slugs
    assert "vue-js" in slugs


def test_max_eight_tags(client, session):
    """Creating an article with more than 8 tags should fail validation."""
    response = client.post(
        "/api/admin/articles",
        json={"title": "Too Many Tags", "content": {}, "tag_names": ["a", "b", "c", "d", "e", "f", "g", "h", "i"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert response.status_code == 422


def test_get_tag_by_slug_returns_tag_and_articles(client, session):
    """GET /api/tags/{slug} should return the tag with its published articles."""
    # Create and publish an article with a tag
    create_response = client.post(
        "/api/admin/articles",
        json={"title": "Docker Guide", "content": {}, "tag_names": ["docker"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    article_id = create_response.json()["id"]
    # Publish it
    client.put(
        f"/api/articles/{article_id}",
        json={"status": "published"},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )

    response = client.get("/api/tags/docker")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "docker"
    assert data["slug"] == "docker"
    assert "articles" in data
    assert len(data["articles"]) == 1
    assert data["articles"][0]["title"] == "Docker Guide"


def test_get_unknown_tag_returns_404(client, session):
    """GET /api/tags/{slug} for a non-existent tag should return 404."""
    response = client.get("/api/tags/nonexistent")
    assert response.status_code == 404


def test_delete_unused_tag_returns_204(client, session):
    """DELETE /api/admin/tags/{id} for an unused tag should return 204."""
    # Create a tag by creating an article, then remove the tag
    create_response = client.post(
        "/api/admin/articles",
        json={"title": "Temp Article", "content": {}, "tag_names": ["temp-tag"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    article_id = create_response.json()["id"]
    tag_id = create_response.json()["tags"][0]["id"]

    # Remove the tag from the article
    client.put(
        f"/api/articles/{article_id}",
        json={"tag_names": []},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )

    # Now delete the unused tag
    response = client.delete(
        f"/api/admin/tags/{tag_id}",
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert response.status_code == 204


def test_delete_used_tag_returns_409(client, session):
    """DELETE /api/admin/tags/{id} for a used tag should return 409 with article count."""
    # Create an article with a tag
    create_response = client.post(
        "/api/admin/articles",
        json={"title": "Tagged Article", "content": {}, "tag_names": ["in-use"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    tag_id = create_response.json()["tags"][0]["id"]

    # Try to delete the used tag
    response = client.delete(
        f"/api/admin/tags/{tag_id}",
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert response.status_code == 409
    data = response.json()
    assert data["detail"]["article_count"] == 1


def test_admin_tags_list_includes_article_counts(client, session):
    """GET /api/admin/tags should include article counts."""
    # Create two articles, one with a tag
    client.post(
        "/api/admin/articles",
        json={"title": "Tagged", "content": {}, "tag_names": ["docker"]},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    client.post(
        "/api/admin/articles",
        json={"title": "Untagged", "content": {}},
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )

    response = client.get(
        "/api/admin/tags",
        headers={"Authorization": "Bearer dev-token-change-in-production"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "docker"
    assert data[0]["article_count"] == 1
