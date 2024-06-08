# ----------------------------------------------------------------------
# Test inv.connectiontypes collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

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


@pytest.fixture(scope="module", params=helper.get_fixture_params(), ids=helper.fixture_id)
def model(request):
    yield helper.get_object(request.param)


def test_uuid_unique(model):
    assert helper.get_uuid_count(model.uuid) == 1, "UUID %s is not unique" % model.uuid


def test_name_unique(model):
    assert helper.get_name_count(model.name) == 1, "Name '%s' is not unique" % model.name


def test_data_format(model):
    if model.data is not None:
        assert isinstance(model.data, list), 'Connection type field "data" must have type "list"'
