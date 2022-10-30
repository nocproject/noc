# ----------------------------------------------------------------------
# Caclulate topology uplinks
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from map.segment import SegmentTopology, logger


def update_uplinks(segment_id: str):
    from noc.inv.models.networksegment import NetworkSegment

    segment = NetworkSegment.get_by_id(segment_id)
    if not segment:
        logger.warning("Segment with id: %s does not exist" % segment_id)
        return
    st = SegmentTopology(segment)
    ManagedObject.update_uplinks(st.iter_uplinks())
