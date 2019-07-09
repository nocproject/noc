# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# test BI dictionaries
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.clickhouse.dictionary import Dictionary


@pytest.fixture(params=list(Dictionary.iter_cls()))
def dictionary(request):
    return request.param


@pytest.mark.dependency(name="test_dictionary_meta")
def test_dictionary_meta(dictionary):
    assert hasattr(dictionary, "_meta")


@pytest.mark.dependency(depends=["test_dictionary_meta"])
def test_dictionary_name(dictionary):
    assert dictionary._meta.name


@pytest.mark.dependency(depends=["test_dictionary_meta"])
def test_dictionary_layout(dictionary):
    assert dictionary._meta.layout


@pytest.mark.dependency(depends=["test_dictionary_meta"])
def test_config(dictionary):
    # @todo: Check result
    assert dictionary.get_config()
