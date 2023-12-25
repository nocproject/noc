# ----------------------------------------------------------------------
# Alcatel.7324RU.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.core.mib import mib


class Script(BaseScript):
    name = "Alcatel.7324RU.get_capabilities"

    # checking "SNMP | MIB | ADSL-MIB" to collect "Interface | xDSL | Line..." metrics
    CHECK_SNMP_GETNEXT = {"SNMP | MIB | ADSL-MIB": mib["ADSL-LINE-MIB::adslLineCoding"]}
