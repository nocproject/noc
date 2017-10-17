# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHInterfaceDescription datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.subinterface import SubInterface


class CHManagedObjectDataSource(BaseDataSource):
    name = "ch_interfacedescription"

    def extract(self):
        mos_id = dict(ManagedObject.objects.filter().values_list("id", "bi_id"))
        for sub in SubInterface.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED,
                                               description__exists=True).scalar("managed_object",
                                                                                "name",
                                                                                "description").order_by("managed_object"):
            yield (
                mos_id[sub.managed_object.id],
                sub.name,
                sub.description.replace("\t", "")
            )
