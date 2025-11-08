# ----------------------------------------------------------------------
# noc.core.url unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.url import URL


@pytest.mark.parametrize(
    ("config", "expected"),
    [("https://user:password@www.www.ru/login", "https://user:password@www.www.ru/login")],
)
def test_url(config, expected):
    assert URL(config).url == expected


@pytest.mark.parametrize(
    ("config", "expected"),
    [("https:///user::password@www.www.ru/login", "https://user:password@www.www.ru/login")],
)
def test_url_error(config, expected):
    with pytest.raises(Exception):
        assert URL(config).url == expected
