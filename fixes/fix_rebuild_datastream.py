# ----------------------------------------------------------------------
# Rebuild datastreams from scratch
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.commands.datastream import Command


def fix():
    for ds in [
        "managedobject",
        "administrativedomain",
        "cfgping",
        "cfgsyslog",
        "cfgtrap",
        "dnszone",
        "address",
        "prefix",
        "vrf",
        "resourcegroup",
    ]:
        Command().run_from_argv(["rebuild", "--datastream", ds])
