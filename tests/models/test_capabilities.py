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

    def __init__(self, caps):
        self.caps = caps

    def save_caps(self, caps):
        self.caps = [
            {
                "capability": str(c.capability.id),
                "value": c.value,
                "source": c.source,
                "scope": c.scope or "",
            }
            for c in caps
        ]


@pytest.mark.parametrize(
    "caps,update_caps,expected",
    [
        ([], {"Cisco | IP | SLA | Probes": 1}, {"Cisco | IP | SLA | Probes": 1}),
        (
            [
                {"key": "Cisco | IP | SLA | Responder", "value": False, "source": "discovery"},
            ],
            {"Cisco | IP | SLA | Probes": 1},
            {"Cisco | IP | SLA | Probes": 1, "Cisco | IP | SLA | Responder": False},
        ),
    ],
)
def test_update_caps(caps, update_caps, expected):
    mock = MockManagedObject([])
    for c in caps:
        mock.set_caps(**c)
    mock.update_caps(update_caps, source="manual")
    assert mock.get_caps() == expected
