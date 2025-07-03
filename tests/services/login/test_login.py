# ----------------------------------------------------------------------
# Test login service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.services.login.auth import get_user_from_cert_subject


@pytest.mark.parametrize(
    ("subj", "expected"),
    [
        ("myuser", "myuser"),
        ("CN=admin,O=Gufo Labs,L=Milano,ST=MI,C=IT", "admin"),
        ("CN=admin", "admin"),
        ("emailAddress=admin@example.com,CN=admin,O=Gufo Labs,L=Milano,ST=MI,C=IT", "admin"),
    ],
)
def test_user_from_cert_subject(subj: str, expected: str) -> None:
    user = get_user_from_cert_subject(subj)
    assert user == expected
