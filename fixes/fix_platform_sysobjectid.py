# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Fill Platform.snmp_sysobjectid
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
# NOC modules
from noc.inv.models.platform import Platform
from noc.sa.models.managedobject import ManagedObject
from noc.core.error import NOCError
from noc.core.mib import mib


def fix():
    for p in Platform.objects.filter():
        if p.snmp_sysobjectid:
            continue  # Already filled
        print("Checked profile: %s" % p.name)
        # Get sample devices
        for mo in ManagedObject.objects.filter(is_managed=True, platform=p.id).order_by("?"):
            caps = mo.get_caps()
            if not caps.get("SNMP"):
                continue
            try:
                v = mo.scripts.get_snmp_get(oid=mib["SNMPv2-MIB::sysObjectID.0"])
            except NOCError:
                continue
            if not v:
                continue
            print("%s sysObjectID.0 %s" % (p.full_name, v))
            p.snmp_sysobjectid = v
            p.save()
            break
