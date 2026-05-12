import pytest
from app.services.permission_service import check_article_permission


class _FakeUser:
    def __init__(self, role: str, is_active: bool = True, user_id: str = "user-1"):
        self.role = role
        self.is_active = is_active
        self.id = user_id


class _FakeArticle:
    def __init__(self, author_id: str = "author-1"):
        self.author_id = author_id


class TestCheckArticlePermission:
    """Test the role × action permission matrix."""

    def test_admin_can_create(self):
        user = _FakeUser(role="admin")
        assert check_article_permission(user, None, "create") is True

    def test_editor_can_create(self):
        user = _FakeUser(role="editor")
        assert check_article_permission(user, None, "create") is True

    def test_contributor_can_create(self):
        user = _FakeUser(role="contributor")
        assert check_article_permission(user, None, "create") is True

    def test_admin_can_edit_own(self):
        user = _FakeUser(role="admin", user_id="admin-1")
        article = _FakeArticle(author_id="admin-1")
        assert check_article_permission(user, article, "edit_own") is True

    def test_contributor_can_edit_own(self):
        user = _FakeUser(role="contributor", user_id="contributor-1")
        article = _FakeArticle(author_id="contributor-1")
        assert check_article_permission(user, article, "edit_own") is True

    def test_contributor_cannot_edit_others(self):
        user = _FakeUser(role="contributor")
        article = _FakeArticle(author_id="someone-else")
        assert check_article_permission(user, article, "edit_others") is False

    def test_editor_can_edit_others(self):
        user = _FakeUser(role="editor")
        article = _FakeArticle(author_id="someone-else")
        assert check_article_permission(user, article, "edit_others") is True

    def test_admin_can_edit_others(self):
        user = _FakeUser(role="admin")
        article = _FakeArticle(author_id="someone-else")
        assert check_article_permission(user, article, "edit_others") is True

    def test_contributor_cannot_delete(self):
        user = _FakeUser(role="contributor")
        article = _FakeArticle(author_id="contributor")
        assert check_article_permission(user, article, "delete") is False

    def test_editor_can_delete(self):
        user = _FakeUser(role="editor")
        article = _FakeArticle(author_id="someone-else")
        assert check_article_permission(user, article, "delete") is True

    def test_admin_can_delete(self):
        user = _FakeUser(role="admin")
        article = _FakeArticle(author_id="someone-else")
        assert check_article_permission(user, article, "delete") is True

    def test_contributor_cannot_publish(self):
        user = _FakeUser(role="contributor")
        article = _FakeArticle(author_id="contributor")
        assert check_article_permission(user, article, "publish") is False

    def test_editor_can_publish(self):
        user = _FakeUser(role="editor")
        article = _FakeArticle(author_id="someone-else")
        assert check_article_permission(user, article, "publish") is True

    def test_admin_can_publish(self):
        user = _FakeUser(role="admin")
        article = _FakeArticle(author_id="someone-else")
        assert check_article_permission(user, article, "publish") is True

    def test_inactive_user_cannot_do_anything(self):
        user = _FakeUser(role="admin", is_active=False, user_id="admin-1")
        article = _FakeArticle(author_id="admin-1")
        assert check_article_permission(user, article, "create") is False
        assert check_article_permission(user, article, "edit_own") is False
        assert check_article_permission(user, article, "edit_others") is False
        assert check_article_permission(user, article, "delete") is False
        assert check_article_permission(user, article, "publish") is False

    def test_unknown_role_cannot_do_anything(self):
        user = _FakeUser(role="unknown", user_id="unknown-1")
        article = _FakeArticle(author_id="unknown-1")
        assert check_article_permission(user, article, "create") is False
        assert check_article_permission(user, article, "edit_own") is False
