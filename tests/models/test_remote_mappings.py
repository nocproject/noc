# ----------------------------------------------------------------------
# Remote Mappings decorator tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
import pytest

# NOC modules
from noc.core.etl.remotemappings import mappings
from noc.main.models.remotesystem import RemoteSystem


@mappings
class MockManagedObject(object):
    name = "mock"
    _is_document = True

    def __init__(self, mappings=None):
        self.mappings = mappings or []

    def update(self, **kwargs):
        """"""


def get_object_caps_mock() -> "MockManagedObject":
    """Prepare ManagedObject for mock"""
    # Send error/send success
    mo = MockManagedObject()
    return mo


@pytest.fixture(scope="function")
def object_caps():
    return get_object_caps_mock()


def test_set_mappings(object_caps):
    rs = RemoteSystem(id=bson.ObjectId(), name="External")
    for _ in range(1, 4):
        object_caps.set_mapping(rs, "1000")
    assert len(object_caps.mappings) == 1
