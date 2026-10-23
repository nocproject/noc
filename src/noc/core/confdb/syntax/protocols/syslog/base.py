# ----------------------------------------------------------------------
# ConfDB protocols syslog syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import IP_ADDRESS

PROTOCOLS_SYSLOG_SYNTAX = DEF(
    "syslog",
    [
        DEF(
            "syslog-server",
            [
                DEF(
                    IP_ADDRESS,
                    [
                        DEF(
                            "source",
                            [
                                DEF(
                                    IP_ADDRESS,
                                    name="source_ip",
                                    gen="make_protocols_syslog_server_source",
                                )
                            ],
                        ),
                    ],
                    name="ip",
                    multi=True,
                    gen="make_protocols_syslog_server",
                )
            ],
        ),
    ],
)
