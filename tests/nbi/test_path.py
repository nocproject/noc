# ----------------------------------------------------------------------
# NBI Path API tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect

# Third-party modules
import pytest

# Python modules
from noc.services.nbi.api.path import (
    Pointer,
    PointerId,
    PointerRemote,
    ObjectPointer,
    InterfacePointer,
    ServicePointer,
    RequestFrom,
    RequestTo,
    RequestConfig,
    RequestConstraints,
    Request,
    MAX_DEPTH_DEFAULT,
    N_SHORTEST_DEFAULT,
)


@pytest.mark.parametrize(
    "interface,value,expected",
    [
        # PointerId
        (PointerId, {}, ValueError),
        (PointerId, {"x": 1}, ValueError),
        (PointerId, {"id": 1}, {"id": "1"}),
        (PointerId, {"id": "1"}, {"id": "1"}),
        # PointerRemote
        (PointerRemote, {}, ValueError),
        (PointerRemote, {"x": 1}, ValueError),
        (PointerRemote, {"remote_system": 1}, ValueError),
        (PointerRemote, {"remote_system": 1, "x": 1}, ValueError),
        (
            PointerRemote,
            {"remote_system": 1, "remote_id": 2},
            {"remote_system": "1", "remote_id": "2"},
        ),
        (
            PointerRemote,
            {"remote_system": "1", "remote_id": "2"},
            {"remote_system": "1", "remote_id": "2"},
        ),
        # Pointer
        (Pointer, {}, ValueError),
        (Pointer, {"x": 1}, ValueError),
        (Pointer, {"id": 1}, {"id": "1"}),
        (Pointer, {"id": "1"}, {"id": "1"}),
        (Pointer, {"remote_system": 1}, ValueError),
        (Pointer, {"remote_system": 1, "x": 1}, ValueError),
        (Pointer, {"remote_system": 1, "remote_id": 2}, {"remote_system": "1", "remote_id": "2"}),
        (
            Pointer,
            {"remote_system": "1", "remote_id": "2"},
            {"remote_system": "1", "remote_id": "2"},
        ),
        # FromObject
        (ObjectPointer, {}, ValueError),
        (ObjectPointer, {"x": 1}, ValueError),
        (ObjectPointer, {"object": 1}, ValueError),
        (ObjectPointer, {"object": {"x": 1}}, ValueError),
        (ObjectPointer, {"object": {"id": 1}}, {"object": {"id": "1"}}),
        (ObjectPointer, {"object": {"remote_system": 1}}, ValueError),
        (
            ObjectPointer,
            {"object": {"remote_system": 1, "remote_id": 2}},
            {"object": {"remote_system": "1", "remote_id": "2"}},
        ),
        (ObjectPointer, {"object": {"id": 1}, "interface": 1}, ValueError),
        (ObjectPointer, {"object": {"id": 1}, "interface": {"x": 1}}, ValueError),
        (
            ObjectPointer,
            {"object": {"id": 1}, "interface": {"name": "Gi 0/1"}},
            {"object": {"id": "1"}, "interface": {"name": "Gi 0/1"}},
        ),
        # From Interface
        (InterfacePointer, {}, ValueError),
        (InterfacePointer, {"x": 1}, ValueError),
        (InterfacePointer, {"interface": 1}, ValueError),
        (InterfacePointer, {"interface": {"x": 1}}, ValueError),
        (InterfacePointer, {"interface": {"id": 1}}, ValueError),
        (
            InterfacePointer,
            {"interface": {"id": "123456789012345678901234"}},
            {"interface": {"id": "123456789012345678901234"}},
        ),
        # From Service
        (ServicePointer, {}, ValueError),
        (ServicePointer, {"x": 1}, ValueError),
        (ServicePointer, {"service": 1}, ValueError),
        (ServicePointer, {"service": {"x": 1}}, ValueError),
        (ServicePointer, {"service": {"id": 1}}, {"service": {"id": "1"}}),
        (ServicePointer, {"service": {"remote_system": 1}}, ValueError),
        (
            ServicePointer,
            {"service": {"remote_system": 1, "remote_id": 2}},
            {"service": {"remote_system": "1", "remote_id": "2"}},
        ),
        # From
        (RequestFrom, {}, ValueError),
        (RequestFrom, {"x": 1}, ValueError),
        (RequestFrom, {"object": 1}, ValueError),
        (RequestFrom, {"object": {"x": 1}}, ValueError),
        (RequestFrom, {"object": {"id": 1}}, {"object": {"id": "1"}}),
        (RequestFrom, {"object": {"remote_system": 1}}, ValueError),
        (
            RequestFrom,
            {"object": {"remote_system": 1, "remote_id": 2}},
            {"object": {"remote_system": "1", "remote_id": "2"}},
        ),
        (RequestFrom, {"object": {"id": 1}, "interface": 1}, ValueError),
        (RequestFrom, {"object": {"id": 1}, "interface": {"x": 1}}, ValueError),
        (
            RequestFrom,
            {"object": {"id": 1}, "interface": {"name": "Gi 0/1"}},
            {"object": {"id": "1"}, "interface": {"name": "Gi 0/1"}},
        ),
        (RequestFrom, {}, ValueError),
        (RequestFrom, {"x": 1}, ValueError),
        (RequestFrom, {"interface": 1}, ValueError),
        (RequestFrom, {"interface": {"x": 1}}, ValueError),
        (RequestFrom, {"interface": {"id": 1}}, ValueError),
        (
            RequestFrom,
            {"interface": {"id": "123456789012345678901234"}},
            {"interface": {"id": "123456789012345678901234"}},
        ),
        (RequestFrom, {}, ValueError),
        (RequestFrom, {"x": 1}, ValueError),
        (RequestFrom, {"service": 1}, ValueError),
        (RequestFrom, {"service": {"x": 1}}, ValueError),
        (RequestFrom, {"service": {"id": 1}}, {"service": {"id": "1"}}),
        (RequestFrom, {"service": {"remote_system": 1}}, ValueError),
        (
            RequestFrom,
            {"service": {"remote_system": 1, "remote_id": 2}},
            {"service": {"remote_system": "1", "remote_id": "2"}},
        ),
        # To
        (RequestTo, {}, ValueError),
        (RequestTo, {"x": 1}, ValueError),
        (RequestTo, {"object": 1}, ValueError),
        (RequestTo, {"object": {"x": 1}}, ValueError),
        (RequestTo, {"object": {"id": 1}}, {"object": {"id": "1"}}),
        (RequestTo, {"object": {"remote_system": 1}}, ValueError),
        (
            RequestTo,
            {"object": {"remote_system": 1, "remote_id": 2}},
            {"object": {"remote_system": "1", "remote_id": "2"}},
        ),
        (RequestTo, {"object": {"id": 1}, "interface": 1}, ValueError),
        (RequestTo, {"object": {"id": 1}, "interface": {"x": 1}}, ValueError),
        (
            RequestTo,
            {"object": {"id": 1}, "interface": {"name": "Gi 0/1"}},
            {"object": {"id": "1"}, "interface": {"name": "Gi 0/1"}},
        ),
        (RequestTo, {}, ValueError),
        (RequestTo, {"x": 1}, ValueError),
        (RequestTo, {"interface": 1}, ValueError),
        (RequestTo, {"interface": {"x": 1}}, ValueError),
        (RequestTo, {"interface": {"id": 1}}, ValueError),
        (
            RequestTo,
            {"interface": {"id": "123456789012345678901234"}},
            {"interface": {"id": "123456789012345678901234"}},
        ),
        (RequestTo, {}, ValueError),
        (RequestTo, {"x": 1}, ValueError),
        (RequestTo, {"service": 1}, ValueError),
        (RequestTo, {"service": {"x": 1}}, ValueError),
        (RequestTo, {"service": {"id": 1}}, {"service": {"id": "1"}}),
        (RequestTo, {"service": {"remote_system": 1}}, ValueError),
        (
            RequestTo,
            {"service": {"remote_system": 1, "remote_id": 2}},
            {"service": {"remote_system": "1", "remote_id": "2"}},
        ),
        # Config
        (RequestConfig, {}, {"max_depth": MAX_DEPTH_DEFAULT, "n_shortest": N_SHORTEST_DEFAULT}),
        (RequestConfig, {"max_depth": 100}, {"max_depth": 100, "n_shortest": N_SHORTEST_DEFAULT}),
        (RequestConfig, {"n_shortest": 15}, {"max_depth": MAX_DEPTH_DEFAULT, "n_shortest": 15}),
        (RequestConfig, {"n_shortest": "15", "max_depth": 20}, {"max_depth": 20, "n_shortest": 15}),
        # Constraints
        (
            RequestConstraints,
            {"vlan": {"vlan": 10}},
            {"upwards": False, "vlan": {"vlan": 10, "strict": False}},
        ),
        (
            RequestConstraints,
            {"vlan": {"interface_untagged": True}},
            {"upwards": False, "vlan": {"interface_untagged": True, "strict": False}},
        ),
        # Request
        (Request, {}, ValueError),
        (
            Request,
            {
                "from": {"object": {"id": 15}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
            },
            {
                "from": {"object": {"id": "15"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
            },
        ),
        (
            Request,
            {
                "from": {"object": {"id": 15}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20},
            },
            {
                "from": {"object": {"id": "15"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20, "n_shortest": N_SHORTEST_DEFAULT},
            },
        ),
        (
            Request,
            {
                "from": {"object": {"id": 15}, "interface": {"name": "Gi 0/1"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20},
            },
            {
                "from": {"object": {"id": "15"}, "interface": {"name": "Gi 0/1"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20, "n_shortest": N_SHORTEST_DEFAULT},
            },
        ),
        (
            Request,
            {
                "from": {"object": {"id": 15}, "interface": {"name": "Gi 0/1"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20},
                "constraints": {"vlan": {"vlan": 10}},
            },
            {
                "from": {"object": {"id": "15"}, "interface": {"name": "Gi 0/1"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20, "n_shortest": N_SHORTEST_DEFAULT},
                "constraints": {"upwards": False, "vlan": {"vlan": 10, "strict": False}},
            },
        ),
        (
            Request,
            {
                "from": {"object": {"id": 15}, "interface": {"name": "Gi 0/1"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20},
                "constraints": {
                    "upwards": False,
                    "vlan": {"interface_untagged": True, "strict": False},
                },
            },
            {
                "from": {"object": {"id": "15"}, "interface": {"name": "Gi 0/1"}},
                "to": {"object": {"remote_system": "20", "remote_id": "25"}},
                "config": {"max_depth": 20, "n_shortest": N_SHORTEST_DEFAULT},
                "constraints": {
                    "upwards": False,
                    "vlan": {"interface_untagged": True, "strict": False},
                },
            },
        ),
    ],
)
def test_interface(interface, value, expected):
    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            interface.clean(value)
    else:
        assert interface.clean(value) == expected
