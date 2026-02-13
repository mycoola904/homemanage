from __future__ import annotations


def is_global_admin(user) -> bool:
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    return bool(user.is_superuser)
