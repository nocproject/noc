# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Network Segment loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from __future__ import absolute_import
# NOC modules
from .base import BaseLoader
from noc.inv.models.networksegment import NetworkSegment
from noc.sa.models.managedobject import ManagedObject


class NetworkSegmentLoader(BaseLoader):
    """
    Network Segment loader
    """
    name = "networksegment"
    model = NetworkSegment
    fields = [
        "id",
        "parent",
        "name",
        "sibling",
        "profile"
    ]

    mapped_fields = {
        "parent": "networksegment",
        "sibling": "networksegment",
        "profile": "networksegmentprofile"
    }

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                for obj in ManagedObject.objects.filter(segment=self.mappings[r_id]):
                    obj.segment = NetworkSegment.objects.get(name="ALL")
                    obj.save()
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []
