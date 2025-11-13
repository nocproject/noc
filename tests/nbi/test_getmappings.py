# ----------------------------------------------------------------------
# NBI getmappings test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import inspect

# Third-party modules
import pytest

# NOC modules
from noc.services.nbi.paths.getmappings import GetMappingsAPI


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        # Empty request must fail
        ({}, ValueError),
        # Missed scope
        ({"id": "10"}, ValueError),
        # Invalid scope
        ({"id": "10", "scope": "invalid"}, ValueError),
        # Check id conversion
        (
            {"scope": "managedobject", "id": 10},
            {
                "scope": "managedobject",
                "local_ids": ["10"],
                "remote_ids": None,
                "remote_system": None,
            },
        ),
        (
            {"scope": "managedobject", "id": "10"},
            {
                "scope": "managedobject",
                "local_ids": ["10"],
                "remote_ids": None,
                "remote_system": None,
            },
        ),
        (
            {"scope": "managedobject", "id": [10]},
            {
                "scope": "managedobject",
                "local_ids": ["10"],
                "remote_ids": None,
                "remote_system": None,
            },
        ),
        (
            {"scope": "managedobject", "id": ["10"]},
            {
                "scope": "managedobject",
                "local_ids": ["10"],
                "remote_ids": None,
                "remote_system": None,
            },
        ),
        (
            {"scope": "managedobject", "id": [10, "11"]},
            {
                "scope": "managedobject",
                "local_ids": ["10", "11"],
                "remote_ids": None,
                "remote_system": None,
            },
        ),
        # Missed remote_system
        ({"scope": "managedobject", "remote_id": 10}, ValueError),
        # No local or remote id
        ({"scope": "managedobject"}, ValueError),
        # Check remote id conversion
        (
            {"scope": "managedobject", "remote_id": 10, "remote_system": "abc"},
            {
                "scope": "managedobject",
                "local_ids": None,
                "remote_ids": ["10"],
                "remote_system": "abc",
            },
        ),
        (
            {"scope": "managedobject", "remote_id": "10", "remote_system": "abc"},
            {
                "scope": "managedobject",
                "local_ids": None,
                "remote_ids": ["10"],
                "remote_system": "abc",
            },
        ),
        (
            {"scope": "managedobject", "remote_id": [10], "remote_system": "abc"},
            {
                "scope": "managedobject",
                "local_ids": None,
                "remote_ids": ["10"],
                "remote_system": "abc",
            },
        ),
        (
            {"scope": "managedobject", "remote_id": [10, "11"], "remote_system": "abc"},
            {
                "scope": "managedobject",
                "local_ids": None,
                "remote_ids": ["10", "11"],
                "remote_system": "abc",
            },
        ),
        # Mixed
        (
            {
                "scope": "managedobject",
                "id": ["55", 56],
                "remote_id": [10, "11"],
                "remote_system": "abc",
            },
            {
                "scope": "managedobject",
                "local_ids": ["55", "56"],
                "remote_ids": ["10", "11"],
                "remote_system": "abc",
            },
        ),
    ],
)
def test_request(input, expected):
    if inspect.isclass(expected) and issubclass(expected, Exception):
        with pytest.raises(expected):
            GetMappingsAPI.cleaned_request(**input)
    else:
        assert GetMappingsAPI.cleaned_request(**input) == expected
