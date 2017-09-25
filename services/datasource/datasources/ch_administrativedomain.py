# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHAdministrativeDomain datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.sa.models.administrativedomain import AdministrativeDomain


class CHAdministrativeDomainDataSource(BaseDataSource):
    name = "ch_administrativedomain"

    def extract(self):
        for ad in AdministrativeDomain.objects.all().order_by("id"):
            yield (
                ad.get_bi_id(),
                ad.id,
                ad.name,
                ad.parent.get_bi_id() if ad.parent else ""
            )
