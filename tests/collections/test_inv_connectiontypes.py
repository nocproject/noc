# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test inv.connectiontypes collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import pytest

# NOC modules
from noc.inv.models.connectiontype import ConnectionType
from .utils import CollectionTestHelper

helper = CollectionTestHelper(ConnectionType)


def teardown_module(module=None):
    """
    Reset all helper caches when leaving module
    :param module:
    :return:
    """
    helper.teardown()


@pytest.fixture(scope="module", params=helper.get_fixture_params(), ids=helper.get_fixture_ids())
def model(request):
    yield helper.get_object(request.param)


@pytest.mark.xfail
def test_uuid_unique(model):
    assert helper.get_uuid_count(model.uuid) == 1, "UUID %s is not unique" % model.uuid
