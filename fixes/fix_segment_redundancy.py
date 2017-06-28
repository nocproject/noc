# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Update segment redundancy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
# NOC modules
from noc.sa.models.objectdata import ObjectData
from noc.sa.models.managedobject import ManagedObject


def fix():
    uplinks = dict(
        (d["_id"], d.get("uplinks", []))
        for d in ObjectData._get_collection().find()
    )
    seg_status = defaultdict(lambda: False)
    for mo in ManagedObject.objects.all():
        u = uplinks.get(mo.id, [])
        seg_status[mo.segment] |= len(u) > 1
    for seg in seg_status:
        seg.set_redundancy(seg_status[seg])
