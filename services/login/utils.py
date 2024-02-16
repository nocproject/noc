# ----------------------------------------------------------------------
# login services utilities.
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.aaa.models.user import User

# As defined in aaa.0002_default_user migration
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "admin"

_SYSTEM_HARDENED = False


def is_hardened() -> bool:
    """
    Check the superuser has default password.

    Returns:
        False if system has default user and password.
    """
    global _SYSTEM_HARDENED

    # Cache positive value
    if _SYSTEM_HARDENED:
        return True
    # Check hardening status
    # Unhardened system has only one user
    if User.objects.count() > 1:
        _SYSTEM_HARDENED = True
        return True
    # Get user
    user = User.objects.first()
    if not user:
        return False  # Fatal state
    # Check user name and password hash
    if user.username == DEFAULT_USER and user.check_password(DEFAULT_PASSWORD):
        return False  # Not hardened
    # Hardened
    _SYSTEM_HARDENED = True
    return True
