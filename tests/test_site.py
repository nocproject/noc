# ----------------------------------------------------------------------
# noc.services.web.base.site test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2028 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC files
from noc.services.web.base.site import site


def test_autodiscover():
    site.autodiscover()
    assert site.apps


@pytest.mark.parametrize(
    ("url", "expected"),
    [("get", "GET"), ("POST", "POST"), ("eViL ", "EVIL"), ("xxx;drop database", "XXXDROPDATABASE")],
)
def test_sanitize_method(url: str, expected: str) -> None:
    assert site.sanitize_method(url) == expected
