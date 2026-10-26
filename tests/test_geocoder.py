# ----------------------------------------------------------------------
# Test noc.core.geocoder
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.geocoder.base import BaseGeocoder, geocoder_loader

GEOCODERS = {"google", "yandex"}


def test_loader_iter_classes() -> None:
    seen = set(geocoder_loader.keys())
    missed = GEOCODERS - seen
    assert not missed, "Missed geocoders: {}".format(", ".join(missed))


@pytest.mark.parametrize("name", list(GEOCODERS))
def test_loader_load(name) -> None:
    cls = geocoder_loader.get(name)
    assert cls is not None
    assert issubclass(cls, BaseGeocoder)
    assert cls.name == name
