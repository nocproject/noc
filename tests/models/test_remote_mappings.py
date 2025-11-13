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
    _created = True

    def __init__(self, mappings=None):
        self.mappings = mappings or []

    def update(self, **kwargs):
        """"""


def get_object_caps_mock() -> "MockManagedObject":
    """Prepare ManagedObject for mock"""
    # Send error/send success
    return MockManagedObject()


@pytest.fixture
def object_mappings():
    return get_object_caps_mock()


def test_set_mappings(object_mappings):
    """"""
    rs = RemoteSystem(id=bson.ObjectId(), name="External")
    for _ in range(1, 4):
        object_mappings.set_mapping(rs, "1000")
    assert len(object_mappings.mappings) == 1
    assert object_mappings.get_mappings() == {rs.name: "1000"}


def test_update_mappings(object_mappings):
    """"""
    rs1 = RemoteSystem(id=bson.ObjectId(), name="External")
    rs2 = RemoteSystem(id=bson.ObjectId(), name="Internal")
    mappings = {rs1: "xxx22", rs2: "xxx234"}
    object_mappings.update_remote_mappings(mappings, source="etl")
    object_mappings.set_mapping(rs1, "xxx22", source="manual")
    assert object_mappings.get_mappings() == {rs1.name: "xxx22", rs2.name: "xxx234"}
    # Remove mappings
    object_mappings.update_remote_mappings({}, source="etl")
    object_mappings.update_remote_mappings({}, source="unknown")
    assert object_mappings.get_mappings() == {rs1.name: "xxx22"}
    object_mappings.update_remote_mappings({}, source="manual")
    assert object_mappings.get_mappings() == {}


def test_master_mappings(object_mappings):
    """"""
    rs1 = RemoteSystem(id=bson.ObjectId(), name="External")
    rs2 = RemoteSystem(id=bson.ObjectId(), name="Internal")
    object_mappings.remote_system = rs1
    object_mappings.remote_id = "xxx23"
    assert object_mappings.get_mappings() == {rs1.name: "xxx23"}
    mappings = {rs1: "xxx23", rs2: "xxx234"}
    object_mappings.update_remote_mappings(mappings, source="etl")
    assert len(object_mappings.mappings) == 2
    object_mappings.update_remote_mappings({}, source="etl")
    assert len(object_mappings.mappings) == 0
    assert object_mappings.get_mappings() == {rs1.name: "xxx23"}
