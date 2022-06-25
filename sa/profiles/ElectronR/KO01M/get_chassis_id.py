# ---------------------------------------------------------------------
# ElectronR.KO01M.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "ElectronR.KO01M.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GET_OIDS = {"SNMP": ["1.3.6.1.4.1.35419.1.1.6.0"]}
