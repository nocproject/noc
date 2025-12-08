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


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("noc.services.web.apps.sa.managedobject.views", "sa.managedobject"),
        ("noc.services.web.apps.sa.managedobject", "sa.managedobject"),
        ("noc.custom.services.web.apps.sa.managedobject.views", "sa.managedobject"),
        ("noc.custom.services.web.apps.sa.managedobject", "sa.managedobject"),
    ],
)
def test_app_id(name: str, expected: str) -> None:
    assert site._get_app_id(name) == expected


@pytest.mark.parametrize(
    "name",
    [
        "noc.services.web.sa.managedobject.views",
        "noc.services.web.sa.managedobject",
        "noc.custom.services.web.sa.managedobject.views",
        "noc.custom.services.web.sa.managedobject",
    ],
)
def test_invalid_app_id(name: str) -> None:
    with pytest.raises(ValueError):
        site._get_app_id(name)
