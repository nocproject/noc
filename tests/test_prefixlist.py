# ----------------------------------------------------------------------
# noc.core.prefixlist unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.prefixlist import optimize_prefix_list, optimize_prefix_list_maxlen


@pytest.mark.parametrize(
    "config, expected",
    [
        (["192.168.128.0/24", "192.168.0.0/16"], ["192.168.0.0/16"]),
        (["192.168.0.0/16", "192.168.128.0/24"], ["192.168.0.0/16"]),
        (["192.168.0.0/24", "192.168.1.0/24"], ["192.168.0.0/23"]),
        (
            ["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"],
            ["192.168.0.0/22"],
        ),
        (["192.168.%d.0/24" % i for i in range(16)], ["192.168.0.0/20"]),
        (["192.168.%d.0/24" % i for i in range(17)], ["192.168.0.0/20", "192.168.16.0/24"]),
        (["192.168.0.0/24", "192.168.0.0/24"], ["192.168.0.0/24"]),
    ],
)
def test_prefixlist(config, expected):
    assert optimize_prefix_list(config) == expected


@pytest.mark.parametrize(
    "config, expected",
    [
        (["192.168.128.0/24", "192.168.0.0/16"], "[(<IPv4 192.168.0.0/16>, 24)]"),
        (["192.168.0.0/16", "192.168.128.0/24"], "[(<IPv4 192.168.0.0/16>, 24)]"),
        (["192.168.0.0/24", "192.168.1.0/24"], "[(<IPv4 192.168.0.0/23>, 24)]"),
        (
            ["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"],
            "[(<IPv4 192.168.0.0/22>, 24)]",
        ),
        (["192.168.%d.0/24" % i for i in range(16)], "[(<IPv4 192.168.0.0/20>, 24)]"),
        (
            ["192.168.%d.0/24" % i for i in range(17)],
            "[(<IPv4 192.168.0.0/20>, 24), (<IPv4 192.168.16.0/24>, 24)]",
        ),
        (["192.168.0.0/24", "192.168.0.0/24"], "[(<IPv4 192.168.0.0/24>, 24)]"),
    ],
)
def test_prefixlist_maxlen(config, expected):
    assert str(optimize_prefix_list_maxlen(config)) == expected
