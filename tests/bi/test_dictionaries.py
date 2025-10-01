# ----------------------------------------------------------------------
# test BI dictionaries
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.bi.dictionaries.loader import loader


@pytest.fixture(params=list(loader.iter_classes()))
def dictionary(request):
    return loader[request.param]


def test_dictionary_meta(dictionary):
    assert hasattr(dictionary, "_meta")


def test_dictionary_name(dictionary):
    assert dictionary._meta.name


def test_dictionary_layout(dictionary):
    assert dictionary._meta.layout


def test_config(dictionary):
    # @todo: Check result
    assert dictionary.get_config()
