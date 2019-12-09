# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test noc.core.geocoder
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.geocoder.base import BaseGeocoder
from noc.core.geocoder.loader import loader

GEOCODERS = {"google", "yandex"}


def test_loader_iter_classes():
    seen = set(loader.iter_classes())
    missed = GEOCODERS - seen
    assert not missed, "Missed geocoders: %s" % ", ".join(missed)


@pytest.mark.parametrize("name", list(GEOCODERS))
def test_loader_load(name):
    cls = loader.get_class(name)
    assert cls is not None
    assert issubclass(cls, BaseGeocoder)
    assert cls.name == name
