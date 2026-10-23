# ----------------------------------------------------------------------
# ConfDB protocols cdp syntax
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from ...defs import DEF
from ...patterns import IF_NAME


PROTOCOLS_CDP_SYNTAX = DEF(
    "cdp",
    [DEF("interface", [DEF(IF_NAME, multi=True, name="interface", gen="make_cdp_interface")])],
)
