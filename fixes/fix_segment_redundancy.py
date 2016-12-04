# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update segment redundancy
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.inv.models.objectuplink import ObjectUplink
from noc.sa.models.managedobject import ManagedObject


def fix():
    uplinks = dict(
        (d["_id"], d["uplinks"])
        for d in ObjectUplink._get_collection().find()
    )
    seg_status = defaultdict(lambda: False)
    for mo in ManagedObject.objects.all():
        u = uplinks.get(mo.id, [])
        seg_status[mo.segment] |= len(u) > 1
    for seg in seg_status:
        seg.set_redundancy(seg_status[seg])
