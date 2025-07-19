# ----------------------------------------------------------------------
# Test Event classifier
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import os
import pytest

# NOC modules
from noc.core.fm.event import Event
from noc.services.classifier.eventconfig import EventConfig, VarItem, FilterConfig
from noc.core.models.valuetype import ValueType
from noc.services.classifier.evfilter.dedup import DedupFilter
from noc.services.classifier.evfilter.suppress import SuppressFilter


event_config = EventConfig(
    name="Network | MAC | MAC Learned",
    bi_id=278863735308143260,
    vars=[
        VarItem(name="mac", type=ValueType.MAC_ADDRESS, required=True, resource_model=None),
        VarItem(name="vlan", type=ValueType.INTEGER, required=False, resource_model=None),
        VarItem(name="interface", type=ValueType.IFACE_NAME, required=False, resource_model=None),
    ],
    event_class="Network | MAC | MAC Learned",
    event_class_id="655519704790c8d4b632a438",
    managed_object_required=True,
    filters={
        "dedup": FilterConfig(window=3, vars=["mac", "interface"]),
        "suppress": FilterConfig(window=3, vars=["mac", "interface"]),
    },
    resources=None,
    actions=None,
)


@pytest.mark.parametrize(
    "events,expected",
    [
        (
            [
                (
                    1751556338,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
                (
                    1751556340,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
                (
                    1751556341,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
                (
                    1751556345,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
            ],
            3,
        )
    ],
)
def test_dedup(events, expected):
    dedup_filter: DedupFilter = DedupFilter()
    r = 0
    path = os.path.realpath(os.path.dirname(__file__))
    with open(os.path.join(path, "events", "mac_events.json"), "rb") as f:
        event = Event.model_validate_json(f.read())
    for ts, event_vars in events:
        event.ts = ts
        de_id = dedup_filter.find(event, event_config, event_vars)
        if not de_id:
            dedup_filter.register(event, event_config, event_vars)
            r += 1
    assert r == expected


@pytest.mark.parametrize(
    "events,expected",
    [
        (
            [
                (
                    1751556338,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
                (
                    1751556340,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
                (
                    1751556341,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
                (
                    1751556345,
                    {
                        "mac": "c0:6d:ed:44:78:44",
                        "interface__ifindex": "27",
                        "vlan": "3080",
                        "ifindex": "27",
                    },
                ),
            ],
            3,
        )
    ],
)
def test_suppress(events, expected):
    suppress_filter: SuppressFilter = SuppressFilter()
    r = 0
    path = os.path.realpath(os.path.dirname(__file__))
    with open(os.path.join(path, "events", "mac_events.json"), "rb") as f:
        event = Event.model_validate_json(f.read())
    for ts, event_vars in events:
        event.ts = ts
        event.vars = event_vars
        de_id = suppress_filter.find(event, event_config)
        if not de_id:
            suppress_filter.register(event, event_config)
            r += 1
    assert r == expected
