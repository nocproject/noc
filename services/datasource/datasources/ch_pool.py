# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHPool datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.main.models.pool import Pool


class CHPoolDataSource(BaseDataSource):
    name = "ch_pool"

    def extract(self):
        for pool in Pool.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED).all().order_by("id"):
            yield (
                pool.bi_id,
                pool.id,
                pool.name
            )
