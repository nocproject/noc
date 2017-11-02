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
        o = Object._get_collection().with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
        for obj in o.find({}, {"_id": 1, "bi_id": 1, "name": 1, "parent": 1}, no_cursor_timeout=True):
            yield (
                obj["bi_id"],
                obj["_id"],
                obj.get("name", ""),
                bi_hash(obj["container"]) if obj.get("container") else ""
            )
