# ----------------------------------------------------------------------
# ConfDB protocols dns syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import ANY, IP_ADDRESS

PROTOCOLS_DNS_SYNTAX = DEF(
    "dns",
    [
        DEF(
            "name-server",
            [DEF(IP_ADDRESS, name="ip", multi=True, gen="make_protocols_dns_name_server")],
        ),
        DEF(
            "search", [DEF(ANY, name="suffix", multi=True, gen="make_protocols_dns_search_suffix")]
        ),
    ],
)
