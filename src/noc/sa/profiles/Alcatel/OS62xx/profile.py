# ----------------------------------------------------------------------
# Vendor: Alcatel
# OS:     OS62xx
# Compatible: OS LS6224
# ----------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.OS62xx"
    pattern_more = [(rb"^More: .*?$", b" ")]
    command_disable_pager = "terminal datadump"
