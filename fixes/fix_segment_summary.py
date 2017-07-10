# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Update segmet summary
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
# NOC modules
from noc.inv.models.networksegment import NetworkSegment


def fix():
    for ns in NetworkSegment.objects.all():
        ns.update_summary()
