# ----------------------------------------------------------------------
# Test inv.protocol collection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.inv.models.protocol import ProtocolVariant, Protocol
from .utils import CollectionTestHelper

helper = CollectionTestHelper(Protocol)


def teardown_module(module=None):
    """
    Reset all helper caches when leaving module
    :param module:
    :return:
    """
    helper.teardown()


@pytest.mark.parametrize(
    "code,expected",
    [
        ("1000BASEZX", ProtocolVariant(Protocol.get_by_code("1000BASEZX"))),
        (">1000BASET", ProtocolVariant(Protocol.get_by_code("1000BASET"), direction=">")),
        (">1000BASEZX-1550", ProtocolVariant(Protocol.get_by_code("1000BASEZX"), ">", "1550")),
        ("1000BASEZX::1550", ProtocolVariant(Protocol.get_by_code("1000BASEZX"), "*", "1550")),
        (">::1000BASEZX::1550", ProtocolVariant(Protocol.get_by_code("1000BASEZX"), ">", "1550")),
        (">1000BASEZX::1550", ProtocolVariant(Protocol.get_by_code("1000BASEZX"), ">", "1550")),
        (">RS485-A", ProtocolVariant(Protocol.get_by_code("RS485"), ">", "A")),
    ],
)
def test_protocol_code(code, expected):
    """
    Test MERGE rule
    :return:
    """
    # Mock segments
    assert ProtocolVariant.get_by_code(code) == expected
