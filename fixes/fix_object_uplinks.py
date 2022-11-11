# ---------------------------------------------------------------------
# Update ObjectUplink
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import progressbar

# NOC modules
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.managedobject import ManagedObject
from noc.core.topology.map.segment import SegmentTopology

BATCH_SIZE = 5000


def iter_ids_batch():
    match = {}
    while True:
        cursor = (
            NetworkSegment._get_collection()
            .find(match, {"_id": 1}, no_cursor_timeout=True)
            .sort("_id")
            .limit(BATCH_SIZE)
        )
        d = [d["_id"] for d in cursor]
        if not d:
            break
        for link in NetworkSegment.objects.filter(id__in=d).timeout(False):
            yield link
        # if match and match["_id"]["$gt"] == d[-1]:
        #     break
        match = {"_id": {"$gt": d[-1]}}


def fix():
    max_value = NetworkSegment._get_collection().estimated_document_count()
    for ns in progressbar.progressbar(iter_ids_batch(), max_value=max_value):
        try:
            st = SegmentTopology(ns)
            ManagedObject.update_uplinks(st.iter_uplinks())
        except Exception as e:
            print("[%s] %s" % (ns.name, e))
