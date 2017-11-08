# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHInterfaceDescription datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

from noc.inv.models.subinterface import SubInterface
from noc.sa.models.managedobject import ManagedObject
from pymongo import ReadPreference

# NOC modules
from .base import BaseDataSource


class CHManagedObjectDataSource(BaseDataSource):
    name = "ch_interfacedescription"

    def extract(self):
        mos_id = dict(ManagedObject.objects.filter().values_list("id", "bi_id"))
        si = SubInterface._get_collection().with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
        for sub in si.find({"description": {"$exists": True}},
                           {"_id": 0, "managed_object": 1, "name": 1, "description": 1}).sort("managed_object"):
            yield (
                mos_id[sub["managed_object"]],
                sub["name"],
                sub["description"]
            )
