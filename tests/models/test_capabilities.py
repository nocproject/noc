# ----------------------------------------------------------------------
# Capabilities decorator tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.caps.decorator import capabilities


@capabilities
class MockManagedObject(object):
    name = "mock"

    def __init__(self, caps=None):
        self.caps = caps or []

    def save_caps(self, caps, **kwargs):
        self.caps = [
            {
                "capability": str(c.capability.id),
                "value": c.value,
                "source": c.source.value,
                "scope": c.scope or "",
            }
            for c in caps
        ]


def get_object_caps_mock() -> "MockManagedObject":
    """Prepare ManagedObject for mock"""
    # Send error/send success
    return MockManagedObject()


@pytest.fixture
def object_caps():
    return get_object_caps_mock()


@pytest.mark.parametrize(
    ("caps", "update_caps", "expected"),
    [
        ([], {"Cisco | IP | SLA | Probes": 1}, {"Cisco | IP | SLA | Probes": 1}),
        (
            [
                {"key": "Cisco | IP | SLA | Responder", "value": False, "source": "discovery"},
                {
                    "key": "Cisco | IP | SLA | Responder",
                    "value": True,
                    "source": "etl",
                    "scope": "RM",
                },
            ],
            {"Cisco | IP | SLA | Probes": 1},
            {"Cisco | IP | SLA | Probes": 1, "Cisco | IP | SLA | Responder": False},
        ),
    ],
)
def test_update_caps(caps, update_caps, expected, object_caps):
    for c in caps:
        object_caps.set_caps(**c)
    object_caps.update_caps(update_caps, source="manual")
    assert object_caps.get_caps() == expected


def test_update_caps_scopes(object_caps):
    object_caps.update_caps({"Cisco | IP | SLA | Probes": 1}, source="manual", scope="scope1")
    object_caps.update_caps({"Cisco | IP | SLA | Probes": 22}, source="manual", scope="scope2")
    assert len(list(object_caps.iter_caps())) == 2
    assert object_caps.get_caps() == {"Cisco | IP | SLA | Probes": 1}


def test_set_caps(object_caps):
    for _ in range(1, 4):
        object_caps.set_caps("DB | Interfaces", 1)
    assert len(object_caps.caps) == 1
    for _ in range(1, 4):
        object_caps.set_caps("CPE | Vendor", "Test1")
    assert len(object_caps.caps) == 2
    object_caps.set_caps("CPE | Vendor", "Test1", scope="New")
    for _ in range(1, 4):
        object_caps.set_caps("CPE | Vendor", "Test1", scope=None)
    assert len(object_caps.caps) == 3


@pytest.mark.parametrize(
    ("caps", "update_caps", "scope", "expected_scope", "expected"),
    [
        (
            [],
            {"Cisco | IP | SLA | Probes": 1},
            None,
            {"Cisco | IP | SLA | Probes": 1},
            {"Cisco | IP | SLA | Probes": 1},
        ),
        (
            [
                {"key": "Cisco | IP | SLA | Responder", "value": False, "source": "discovery"},
                {
                    "key": "Cisco | IP | SLA | Responder",
                    "value": True,
                    "source": "etl",
                    "scope": "RM",
                },
            ],
            {"Cisco | IP | SLA | Probes": 1},
            "RM",
            {"Cisco | IP | SLA | Probes": 1},
            {"Cisco | IP | SLA | Probes": 1, "Cisco | IP | SLA | Responder": False},
        ),
    ],
)
def test_get_scope_caps(caps, update_caps, scope, expected_scope, expected, object_caps):
    for c in caps:
        object_caps.set_caps(**c)
    object_caps.update_caps(update_caps, source="manual", scope=scope)
    assert object_caps.get_caps(scope=scope) == expected_scope
    assert object_caps.get_caps() == expected
