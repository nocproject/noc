# ----------------------------------------------------------------------
# Test inv.objectmodels collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.protocol import ProtocolVariant
from .utils import CollectionTestHelper

from noc.core.mongo.connection import connect

connect()

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
    fail = []
    for c in model.connections:
        if c.gender not in c.type.genders:
            valid_genders = ", ".join(f"'{x}'" for x in c.type.genders)
            fail.append(f"{c.name}: Invalid gender '{c.gender}' (Must be in {valid_genders})")
    if fail:
        pytest.fail("\n".join(fail))


def test_data_format(model):
    if model.data is not None:
        assert isinstance(model.data, list), 'Object model field "data" must have type "list"'


def test_connection_direction(model: ObjectModel) -> None:
    fail = []
    for c in model.connections:
        checklist = CONNECTION_CHECKLIST.get(c.type.name)
        if not checklist:
            continue
        if c.direction and "directions" in checklist:
            if c.direction not in checklist["directions"]:
                valid_directions = ", ".join("'%s'" % x for x in directions)
                fail.append(
                    f"{c.name}: Invalid direction '{c.direction}' (Must be in {valid_directions})"
                )
    if fail:
        pytest.fail("\n".join(fail))


def test_connection_protocols(model: ObjectModel) -> None:
    if model.get_data("length", "length"):
        pytest.skip("is wire")
    fail = []
    for c in model.connections:
        checklist = CONNECTION_CHECKLIST.get(c.type.name)
        if not checklist:
            continue
        if "protocols" in checklist:
            p_checks = _CT_PROTOCOLS.get(c.type.name)
            if p_checks is None:
                p_checks = [ProtocolVariant.get_by_code(p) for p in checklist["protocols"]]
                _CT_PROTOCOLS[c.type.name] = p_checks
            if not any(p in p_checks for p in c.protocols):
                valid_protocols = ", ".join(f"'{x}'" for x in checklist["protocols"])
                fail.append(f"{c.name}: Must have at least one of protocols {valid_protocols}")
    if fail:
        pytest.fail("\n".join(fail))


_CT_PROTOCOLS = {}

# dict must have one or more keys:
# * direction - list of possible directions
# * protocols - list of possible protocols. At least one protocol must be met
CONNECTION_CHECKLIST = {
    "Electrical | DB9": {
        "directions": "s",
        "protocols": [">RS232", ">DryContact", "<RS232", "<RS485-A", "<RS485-B"],
    },
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
            "G703",
            "ToD",
            "E&M",  # Telephony E&M over PBX
            "IEEE1588",
            "TL1",
            "ADSL",
        ],
    },
    "Electrical | SFF-8470": {"directions": "s", "protocols": ["10GBASECX4"]},
    "Electrical | CXP": {
        "directions": "s",
        "protocols": [
            "40GBASECR4",
            "100GBASESR2",
            "100GBASECR4",
            "100GBASESR4",
            "100GBASEKR4",
            "100GBASEKP4",
            "100GBASECR10",
            "100GBASESR10",
        ],
    },
    "Electrical | Power | IEC 60320 C14": {
        "directions": "s",
        "protocols": [">220VAC", "<220VAC", ">110VAC", "<110VAC"],
    },
    "Electrical | Power | IEC 60320 C16": {
        "directions": "s",
        "protocols": [">220VAC", "<220VAC", ">110VAC", "<110VAC"],
    },
    "Electrical | Power | IEC 60320 C20": {
        "directions": "s",
        "protocols": [">220VAC", "<220VAC", ">110VAC", "<110VAC"],
    },
    "Transceiver | GBIC": {"directions": ["i", "o"], "protocols": ["TransEth100M", "TransEth1G"]},
    "Transceiver | SFP": {
        "directions": ["i", "o"],
        "protocols": ["TransEth100M", "TransEth1G", "GPON"],
    },
    "Transceiver | SFP | Cisco": {
        "directions": ["i", "o"],
        "protocols": ["TransEth100M", "TransEth1G", "GPON"],
    },
    "Transceiver | SFP+": {
        "directions": ["i", "o"],
        "protocols": [
            "TransEth1G",
            "TransEth10G",
            "OTU1",
            "OTU2",
        ],
    },
    "Transceiver | SFP+ | Cisco": {
        "directions": ["i", "o"],
        "protocols": ["TransEth1G", "TransEth10G"],
    },
    "Transceiver | SFP+ | Force10": {
        "directions": ["i", "o"],
        "protocols": ["TransEth1G", "TransEth10G"],
    },
    "Transceiver | SFP+ | Juniper": {
        "directions": ["i", "o"],
        "protocols": ["TransEth1G", "TransEth10G"],
    },
    "Transceiver | SFP28": {
        "directions": ["i", "o"],
        "protocols": ["TransEth10G", "TransEth25G"],
    },
    "Transceiver | SFP56": {
        "directions": ["i", "o"],
        "protocols": ["TransEth50G"],
    },
    "Transceiver | QSFP": {
        "directions": ["i", "o"],
        "protocols": ["TransEth1G", "TransEth4G"],
    },
    "Transceiver | QSFP+": {
        "directions": ["i", "o"],
        "protocols": ["TransEth10G", "TransEth40G", "TransEth100G"],
    },
    "Transceiver | QSFP14": {
        "directions": ["i", "o"],
        "protocols": ["TransEth50G"],
    },
    "Transceiver | QSFP28": {
        "directions": ["i", "o"],
        "protocols": ["TransEth10G", "TransEth40G", "TransEth50G", "TransEth100G"],
    },
    "Transceiver | QSFP56": {
        "directions": ["i", "o"],
        "protocols": ["TransEth10G", "TransEth40G", "TransEth100G", "TransEth200G"],
    },
    "Transceiver | QSFP-DD": {
        "directions": ["i", "o"],
        "protocols": ["TransEth10G", "TransEth40G", "TransEth100G", "TransEth200G", "TransEth400G"],
    },
    "Transceiver | OSFP": {
        "directions": ["i", "o"],
        "protocols": ["TransEth400G", "TransEth800G"],
    },
    "Transceiver | XFP": {"directions": ["i", "o"], "protocols": ["TransEth10G"]},
    "Transceiver | XFP | Cisco": {
        "directions": ["i", "o"],
        "protocols": ["TransEth10G"],
    },
    "Transceiver | XENPAK | Cisco": {"directions": ["i", "o"], "protocols": ["TransEth10G"]},
    "Transceiver | X2 | Cisco": {"directions": ["i", "o"], "protocols": ["TransEth10G"]},
    "Transceiver | CFP": {
        "directions": ["i", "o"],
        "protocols": ["TransEth40G", "TransEth100G"],
    },
    "Transceiver | CFP2": {
        "directions": ["i", "o"],
        "protocols": [
            "TransEth40G",
            "TransEth100G",
            "TransEth200G",
            "OTU1",
            "OTU2",
            "OTU2e",
            "OTU3",
            "OTU4",
        ],
    },
    "Transceiver | CFP4": {
        "directions": ["i", "o"],
        "protocols": ["TransEth40G", "TransEth100G"],
    },
    "Transceiver | CFP8": {
        "directions": ["i", "o"],
        "protocols": [
            "TransEth40G",
            "TransEth100G",
            "TransEth200G",
            "TransEth400G",
        ],
    },
}
