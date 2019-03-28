# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.RCIOS.get_interface_status_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_status_ex import Script as BaseScript
from noc.sa.interfaces.igetinterfacestatusex import IGetInterfaceStatusEx


class Script(BaseScript):
    name = "Raisecom.RCIOS.get_interface_status_ex"
    interface = IGetInterfaceStatusEx

    MAX_REPETITIONS = 10
    MAX_GETNEXT_RETIRES = 0

    IFNAME_OID = "IF-MIB::ifDescr"
