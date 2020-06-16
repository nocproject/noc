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
from noc.sa.models.objectdata import ObjectData
from noc.core.topology.segment import SegmentTopology


def fix():
    total = NetworkSegment._get_collection().estimated_document_count()
    for ns in progressbar.progressbar(NetworkSegment.objects.timeout(False), max_value=total):
        st = SegmentTopology(ns)
        ObjectData.update_uplinks(st.iter_uplinks())
