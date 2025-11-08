# ----------------------------------------------------------------------
# Test BaseNormalizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.confdb.normalizer.base import BaseNormalizer, match, ANY, REST
from noc.core.ip import IPv4

CONF1 = [
    ["hostname", "test"],
    ["interface", "e0"],
    ["interface", "e0", "description", "test"],
    ["interface", "e0", "ip", "address", "10.0.0.1", "255.255.255.0"],
]

RESULT1 = [
    ("system", "hostname", "test", {"replace": True}),
    ("interfaces", "e0", "description", "test", {"replace": True}),
    (
        "virtual-router",
        "default",
        "forwarding-instance",
        "default",
        "interfaces",
        "e0",
        "unit",
        "0",
        "inet",
        "address",
        IPv4("10.0.0.1/24"),
    ),
]


class Normalizer1(BaseNormalizer):
    @match("hostname", ANY)
    def normalize_hostname(self, tokens):
        yield self.make_hostname(tokens[1])

    @match("interface", ANY, "description", REST)
    def normalize_interface_description(self, tokens):
        yield self.make_interface_description(interface=tokens[1], description=" ".join(tokens[3:]))

    @match("interface", ANY, "ip", "address", ANY, ANY)
    def normalize_interface_address(self, tokens):
        yield self.make_unit_inet_address(
            interface=tokens[1], address=self.to_prefix(tokens[4], tokens[5])
        )


@pytest.mark.parametrize(("tokens", "ncls", "result"), [(CONF1, Normalizer1, RESULT1)])
def test_normalizer(tokens, ncls, result):
    normalizer = ncls(None, tokens)
    assert list(normalizer) == result
