# ----------------------------------------------------------------------
# Subscriber loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseLoader
from ..models.subscriber import Subscriber
from noc.crm.models.subscriberprofile import SubscriberProfile
from noc.crm.models.subscriber import Subscriber as SubscriberModel


class SubscriberLoader(BaseLoader):
    """
    Administrative division loader
    """

    name = "subscriber"
    model = SubscriberModel
    data_model = Subscriber
    model_mappings = {"profile": SubscriberProfile}

    discard_deferred = True

    def find_object(self, v):
        """
        Find object by remote system/remote id
        :param v:
        :return:
        """
        if not v.get("remote_system") or not v.get("remote_id"):
            self.logger.warning("RS or RID not found")
            return None
        if not hasattr(self, "_subscriber_remote_ids"):
            self.logger.info("Filling service collection")
            coll = SubscriberModel._get_collection()
            self._subscriber_remote_ids = {
                c["remote_id"]: c["_id"]
                for c in coll.find(
                    {"remote_system": v["remote_system"].id, "remote_id": {"$exists": True}},
                    {"remote_id": 1, "_id": 1},
                )
            }
        if v["remote_id"] in self._subscriber_remote_ids:
            return SubscriberModel.objects.get(id=self._subscriber_remote_ids[v["remote_id"]])
        return None
