# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Set SNMP | v2c capability if SNMP cap is set
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.models.managedobject import ManagedObject


def fix():
    for mo in ManagedObject.objects.all():
        caps = mo.get_caps()
        if caps.get("SNMP") and not caps.get("SNMP | v1") and not caps.get("SNMP | v2c"):
            mo.update_caps({
                "SNMP | v2c": True
            }, source="caps")
