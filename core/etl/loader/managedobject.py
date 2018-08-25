# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Managed Object loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from base import BaseLoader
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool
from noc.sa.models.profile import Profile


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
        "termination_group",
        "service_terminator",
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
        "termination_group": "terminationgroup",
        "service_terminator": "terminationgroup",
        "container": "container",
        "auth_profile": "authprofile",
        "tt_system": "ttsystem"
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
