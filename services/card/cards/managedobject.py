# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseCard
from noc.sa.models.managedobject import ManagedObject


class ManagedObjectCard(BaseCard):
    default_template_name = "managedobject"

    def find(self, id=None, **kwargs):
        q = {}
        if id:
            q["pk"] = int(id)
        if not q:
            return None
        try:
            return ManagedObject.objects.get(**q)
        except ManagedObject.DoesNotExist:
            return None

    def get_template_name(self):
        return self.object.object_profile.card or "managedobject"

    def get_data(self):
        # @todo: Container
        # @todo: Uptime
        # @todo: Stage
        # @todo: Service range
        # @todo: Neighbors
        # @todo: Open TT
        r = {
            "id": self.object.id,
            "name": self.object.name,
            "address": self.object.address,
            "platform": self.object.platform or "Unknown",
            "version": self.object.version,
            "description": self.object.description,
            "object_profile": self.object.object_profile.id,
            "object_profile_name": self.object.object_profile.name,
            "interfaces": []
        }
        # @todo: admin status, oper status, speed/duplex, errors in/out,
        # @todo: vlan/mac, service
        return r
