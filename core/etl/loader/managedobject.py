# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Managed Object loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import BaseLoader
from noc.sa.models.managedobject import ManagedObject
from noc.main.models.pool import Pool


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
        "profile_name",
        "object_profile",
        "termination_group",
        "service_terminator",
        "scheme",
        "address",
        "port",
        "user",
        "password",
        "super_password",
        "snmp_ro"
    ]

    mapped_fields = {
        "administrative_domain": "administrativedomain",
        "object_profile": "managedobjectprofile",
        "segment": "networksegment",
        "termination_group": "terminationgroup",
        "container": "container"
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
        return v
