# ----------------------------------------------------------------------
# Password policy checker
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.translation import ugettext as _
from noc.config import config
from .hasher import check_password


def check_password_policy(
    password: str,
    /,
    min_password_len: int | None = None,
    min_password_uppercase: int | None = None,
    min_password_lowercase: int | None = None,
    min_password_numbers: int | None = None,
    min_password_specials: int | None = None,
    history: list[str] | None = None,
) -> None:
    """
    Check password compliance to the policy.

    Validate password again policy
    and raise ValueError if policy is violated.

    Args:
        password: Password to check.
        min_password_len: Minimal password length.
            Use `config.login.min_password_len` if not set.
        min_password_uppercase: Required amount of uppercase letters in password.
            Use `config.login.min_password_uppercase` if not set.
        min_password_lowercase: Required amount of lowercase letters in password.
            Use `config.login.min_password_lowercase` if not set.
        min_password_numbers: Required amount of numbers in password.
            Use `config.login.min_password_numbers` if not set.
        min_password_specials: Required amount of special characters in password.
            Use `config.login.min_password_specials` if not set.
        history: List of previous hashes.

    Raises:
        ValueError: if password policy is violated.
    """
    _check_len(password, min_password_len)
    _check_uppercase(password, min_password_uppercase)
    _check_lowercase(password, min_password_lowercase)
    _check_numbers(password, min_password_numbers)
    _check_specials(password, min_password_specials)
    _check_history(password, history)


def _check_len(password: str, limit: int | None) -> None:
    """Check password length."""

    if limit is None:
        limit = config.login.min_password_len
    if len(password) < limit:
        msg = _("Password too short. Must be %d characters or longer") % limit
        raise ValueError(msg)


def _check_uppercase(password: str, limit: int | None) -> None:
    """Check password has required uppercase letters."""
    if limit is None:
        limit = config.login.min_password_uppercase
    if limit < 1:
        return
    n = sum(1 for c in password if c.isupper())
    if n < limit:
        msg = _("Password must have at least %d upper-case letters") % limit
        raise ValueError(msg)


def _check_lowercase(password: str, limit: int | None) -> None:
    """Check password has required lowercase letters."""
    if limit is None:
        limit = config.login.min_password_lowercase
    if limit < 1:
        return
    n = sum(1 for c in password if c.islower())
    if n < limit:
        msg = _("Password must have at least %d lower-case letters") % limit
        raise ValueError(msg)


def _check_numbers(password: str, limit: int | None) -> None:
    """Check password has required numbers."""
    if limit is None:
        limit = config.login.min_password_numbers
    if limit < 1:
        return
    n = sum(1 for c in password if c.isdigit())
    if n < limit:
        msg = _("Password must have at least %d numbers") % limit
        raise ValueError(msg)


def _check_specials(password: str, limit: int | None) -> None:
    """Check password has required special symbols."""
    if limit is None:
        limit = config.login.min_password_specials
    if limit < 1:
        return
    n = sum(1 for c in password if not c.isalnum())
    if n < limit:
        msg = _("Password must have at least %d special symbols") % limit
        raise ValueError(msg)


def _check_history(password: str, history: list[str] | None) -> None:
    """Check password history."""
    if not history:
        return
    for h in history:
        if check_password(password, h):
            msg = _("Password is already used")
            raise ValueError(msg)
