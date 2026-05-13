PERMISSIONS = {
    "admin": {"create", "edit_own", "edit_others", "delete", "publish", "reassign"},
    "editor": {"create", "edit_own", "edit_others", "delete", "publish"},
    "contributor": {"create", "edit_own", "delete"},
}


def check_article_permission(user, article, action: str) -> bool:
    if not getattr(user, "is_active", False):
        return False

    role = getattr(user, "role", "")
    allowed_actions = PERMISSIONS.get(role, set())

    if action not in allowed_actions:
        return False

    if action in ("edit_own", "delete") and article is not None and role == "contributor":
        return str(article.author_id) == str(getattr(user, "id", ""))

    return True
