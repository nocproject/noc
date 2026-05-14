# ---------------------------------------------------------------------
# CleverElectronic.MPDU.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "CleverElectronic.MPDU.get_fqdn"
    interface = IGetFQDN

    SNMP_SYSNAME_OID = "1.3.6.1.4.1.30966.8.1.1.1.0"
