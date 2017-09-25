# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHPlatform datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.inv.models.platform import Platform


class CHPlatformDataSource(BaseDataSource):
    name = "ch_platform"

    def extract(self):
        for p in Platform.objects.all().order_by("id"):
            yield (
                p.get_bi_id(),
                p.id,
                p.name,
                p.vendor.name,
                "%s %s" % (p.vendor.name, p.name)
            )
