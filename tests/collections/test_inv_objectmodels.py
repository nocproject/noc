# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test inv.objectmodels collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import pytest

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from .utils import CollectionTestHelper

helper = CollectionTestHelper(ObjectModel)


@pytest.fixture(scope="module", params=helper.get_fixture_params(), ids=helper.get_fixture_ids())
def model(request):
    yield helper.get_object(request.param)


@pytest.mark.xfail
def test_cr_context(model):
    if model.connection_rule is None:
        pytest.skip("No connection rule")
    assert model.cr_context is not None, "'cr_context' must be filled"


@pytest.mark.xfail
def test_connection_gender(model):
    for c in model.connections:
        with pytest.assume:
            assert c.gender in c.type.genders, "%s: Invalid gender '%s' (Must be in %s)" % (
                c.name,
                c.gender,
                ", ".join("'%s'" % x for x in c.type.genders),
            )


def check_direction(c, directions):
    __tracebackhide__ = True
    if c.direction not in directions:
        pytest.fail(
            "%s: Invalid direction '%s' (Must be in %s)"
            % (c.name, c.direction, ", ".join("'%s'" % x for x in directions))
        )


def check_protocols(c, protocols):
    __tracebackhide__ = True
    if not any(True for p in c.protocols if p in protocols):
        pytest.fail(
            "%s: Must have at least one of protocols %s"
            % (c.name, ", ".join("'%s'" % x for x in protocols))
        )


@pytest.mark.xfail
def test_connection_checklist(model):
    for c in model.connections:
        checklist = CONNECTION_CHECKLIST.get(c.type.name)
        if not checklist:
            continue
        if c.direction and "direction" in checklist:
            with pytest.assume:
                check_direction(c, checklist["directions"])
        if "protocols" in checklist:
            with pytest.assume:
                check_protocols(c, checklist["protocols"])


# dict must have one or more keys:
# * direction - list of possible directions
# * protocols - list of possible protocols. At least one protocol must be met
CONNECTION_CHECKLIST = {
    "Electrical | DB9": {"direction": "s", "protocols": [">RS232"]},
    "Electrical | RJ45": {
        "directions": "s",
        "protocols": [
            "10BASET",
            "100BASETX",
            "1000BASET",
            "2.5GBASET",
            "5GBASET",
            "10GBASET",
            ">RS232",
            ">DryContact",
        ],
    },
    "Electrical | Power | IEC 60320 C14": {
        "direction": "s",
        "protocols": [">220VAC", "<220VAC", ">110VAC", "<110VAC"],
    },
}
