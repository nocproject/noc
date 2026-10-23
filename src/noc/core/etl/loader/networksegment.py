# ----------------------------------------------------------------------
# Network Segment loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from noc.inv.models.networksegment import NetworkSegment as NetworkSegmentModel
from noc.inv.models.networksegmentprofile import NetworkSegmentProfile
from noc.sa.models.managedobject import ManagedObject
from ..models.networksegment import NetworkSegment


class NetworkSegmentLoader(BaseLoader):
    """
    Network Segment loader
    """

    name = "networksegment"
    model = NetworkSegmentModel
    data_model = NetworkSegment
    model_mappings = {"profile": NetworkSegmentProfile}

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                for obj in ManagedObject.objects.filter(segment=self.mappings[r_id]):
                    obj.segment = NetworkSegmentModel.objects.get(name="ALL")
                    obj.save()
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []
