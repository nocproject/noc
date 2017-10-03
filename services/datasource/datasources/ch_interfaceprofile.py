# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHInterfaceProfile datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.inv.models.interfaceprofile import InterfaceProfile


class CHInterfaceProfileDataSource(BaseDataSource):
    name = "ch_interfaceprofile"

    def extract(self):
        for p in InterfaceProfile.objects.all(read_preference=ReadPreference.SECONDARY_PREFERRED).order_by("id"):
            yield (
                p.bi_id,
                p.id,
                p.name,
                1 if p.is_uni else 0
            )
