# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Container datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.inv.models.object import Object
from noc.core.bi.decorator import bi_hash


class CHContainerDataSource(BaseDataSource):
    name = "ch_container"

    def extract(self):
        for obj in Object.objects.all(read_preference=ReadPreference.SECONDARY_PREFERRED).order_by("id"):
            yield (
                obj.bi_id,
                obj.id,
                obj.name,
                bi_hash(obj.container) if obj.container else ""
            )
