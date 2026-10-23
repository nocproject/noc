# ---------------------------------------------------------------------
# Update segment redundancy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.sa.models.managedobject import ManagedObject


def fix():
    seg_status = defaultdict(lambda: False)
    for mo in ManagedObject.objects.all():
        u = mo.uplinks or []
        seg_status[mo.segment] |= len(u) > 1
    for seg in seg_status:
        seg.set_redundancy(seg_status[seg])
