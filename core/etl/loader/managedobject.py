# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from .base import BaseLoader


class ManagedObjectLoader(BaseLoader):
    """
    Managed Object loader
    """
    name = "managedobject"
    model = ManagedObject
    fields = [
        "id",
        "name",
        "is_managed",
        "container",
        "administrative_domain",
        "pool",
        "segment",
        "profile",
        "object_profile",
        "static_client_groups",
        "static_service_groups",
        "scheme",
        "address",
        "port",
        "user",
        "password",
        "super_password",
        "snmp_ro",
        "description",
        "auth_profile",
        "tags",
        "tt_system",
        "tt_queue",
        "tt_system_id"
    ]

    mapped_fields = {
        "administrative_domain": "administrativedomain",
        "object_profile": "managedobjectprofile",
        "segment": "networksegment",
        "container": "container",
        "auth_profile": "authprofile",
        "tt_system": "ttsystem",
        "static_client_groups": "resourcegroup",
        "static_service_groups": "resourcegroup"
    }

    def __init__(self, *args, **kwargs):
        super(ManagedObjectLoader, self).__init__(*args, **kwargs)
        self.pools = dict((p.name, p) for p in Pool.objects.all())

    def clean(self, row):
        """
        Fix pool
        """
        v = super(ManagedObjectLoader, self).clean(row)
        v["pool"] = self.pools[v["pool"]]
        if "tags" in v:
            v["tags"] = [x.strip().strip('"') for x in v["tags"].split(",")
                         if x.strip()] if v["tags"] else []
        v["profile"] = Profile.get_by_name(v["profile"])
        v["static_client_groups"] = [v["static_client_groups"]] if v["static_client_groups"] else []
        v["static_service_groups"] = [v["static_service_groups"]] if v["static_service_groups"] else []
        return v

    def purge(self):
        """
        Perform pending deletes
        """
        for r_id, msg in reversed(self.pending_deletes):
            self.logger.debug("Deactivating: %s", msg)
            self.c_delete += 1
            try:
                obj = self.model.objects.get(pk=self.mappings[r_id])
                obj.is_managed = False
                obj.container = None
                obj.save()
            except self.model.DoesNotExist:
                pass  # Already deleted
        self.pending_deletes = []
