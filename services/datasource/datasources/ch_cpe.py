# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHCPEAttributes datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.sa.models.cpestatus import CPEStatus


class CHInterfaceAttributesDataSource(BaseDataSource):
    name = "ch_cpe"

    def extract(self):
        # mos_id = dict(ManagedObject.objects.filter().values_list("id", "bi_id"))
        for cpe in CPEStatus.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED):
            yield (
                cpe.managed_object.bi_id,
                cpe.global_id,
                cpe.interface,
                cpe.local_id,
                cpe.global_id,
                cpe.name,
                cpe.type,
                cpe.vendor,
                cpe.model,
                cpe.version,
                cpe.serial,
                cpe.ip,
                cpe.mac,
                cpe.description,
                cpe.location,
                cpe.distance
            )
