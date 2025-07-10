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
    def __init__(self, caps):
        self.caps = caps

    def save_caps(self, caps):
        """"""


@pytest.mark.parametrize(
    "caps,update_caps,expected",
    [
        ([], {"Cisco | IP | SLA | Probes": 1}, {"Cisco | IP | SLA | Probes": 1}),
        (
            [
                {"capabilities": "Cisco | IP | SLA | Responder", "value": 2, "source": "discovery"},
            ],
            {"Cisco | IP | SLA | Probes": 1},
            {"Cisco | IP | SLA | Probes": 1, "Cisco | IP | SLA | Responder": 2},
        ),
    ],
)
def test_update_caps(caps, update_caps, expected):
    mock = MockManagedObject(caps)
    mock.update_caps(update_caps)
    assert mock.get_caps() == expected
