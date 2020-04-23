# ----------------------------------------------------------------------
# Test inv.objectmodels collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from .utils import CollectionTestHelper

helper = CollectionTestHelper(ObjectModel)


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


def test_cr_context(model):
    if model.connection_rule is None:
        pytest.skip("No connection rule")
    assert model.cr_context is not None, "'cr_context' must be filled"


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


def test_connection_checklist(model):
    for c in model.connections:
        checklist = CONNECTION_CHECKLIST.get(c.type.name)
        if not checklist:
            continue
        if c.direction and "directions" in checklist:
            with pytest.assume:
                check_direction(c, checklist["directions"])
        if "protocols" in checklist:
            with pytest.assume:
                check_protocols(c, checklist["protocols"])


# dict must have one or more keys:
# * direction - list of possible directions
# * protocols - list of possible protocols. At least one protocol must be met
CONNECTION_CHECKLIST = {
    "Electrical | DB9": {"directions": "s", "protocols": [">RS232", ">DryContact"]},
    "Electrical | RJ45": {
        "directions": "s",
        "protocols": [
            "10BASET",
            "100BASETX",
            "1000BASET",
            "1000BASETX",
            "2.5GBASET",
            "5GBASET",
            "10GBASET",
            ">RS232",
            ">RS485",
            ">DryContact",
            "G.703",
            "ToD",
            "EM",  # Telephony E&M over PBX
            ">TL1",
            "IEEE1588",
            "ADSLoPOTS",
        ],
    },
    "Electrical | Power | IEC 60320 C14": {
        "directions": "s",
        "protocols": [">220VAC", "<220VAC", ">110VAC", "<110VAC"],
    },
}
