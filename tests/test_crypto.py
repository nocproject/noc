# ----------------------------------------------------------------------
# noc.core.crypto test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.crypto import gen_salt, md5crypt


@pytest.mark.parametrize(("raw", "value"), [(4, 4), (10, 10)])
def test_salt_length(raw, value):
    salt = gen_salt(raw)
    assert isinstance(salt, bytes)
    assert len(salt) == value


@pytest.mark.parametrize(
    ("raw", "value"),
    [
        ({"password": "test", "salt": "1234"}, b"$1$1234$InX9CGnHSFgHD3OZHTyt3."),
        ({"password": "test", "salt": "1234", "magic": "$5$"}, b"$5$1234$x29w4cwzSDnesjss/m2O1."),
    ],
)
def test_md5_crypt(raw, value):
    assert md5crypt(**raw) == value
