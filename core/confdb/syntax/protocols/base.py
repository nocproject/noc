# ----------------------------------------------------------------------
# ConfDB protocols syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ..defs import DEF
from .ntp.base import PROTOCOLS_NTP_SYNTAX
from .cdp.base import PROTOCOLS_CDP_SYNTAX
from .lldp.base import PROTOCOLS_LLDP_SYNTAX
from .spanningtree.base import PROTOCOLS_SPANNING_TREE_SYNTAX
from .udld.base import PROTOCOLS_UDLD_SYNTAX
from .loopdetect.base import PROTOCOLS_LOOP_DETECT_SYNTAX
from .lacp.base import PROTOCOLS_LACP_SYNTAX
from .dns.base import PROTOCOLS_DNS_SYNTAX


PROTOCOLS_SYNTAX = DEF(
    "protocols",
    [
        PROTOCOLS_NTP_SYNTAX,
        PROTOCOLS_CDP_SYNTAX,
        PROTOCOLS_LLDP_SYNTAX,
        PROTOCOLS_UDLD_SYNTAX,
        PROTOCOLS_SPANNING_TREE_SYNTAX,
        PROTOCOLS_LOOP_DETECT_SYNTAX,
        PROTOCOLS_LACP_SYNTAX,
        PROTOCOLS_DNS_SYNTAX,
    ],
)
