# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Fix PoP links
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.objectuplink import ObjectUplink
from noc.core.topology.segment import SegmentTopology

from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object


def fix():
    pop_models =


    for ns in NetworkSegment.objects.all():
        st = SegmentTopology(ns)
        ObjectUplink.update_uplinks(
            st.get_object_uplinks()
        )
