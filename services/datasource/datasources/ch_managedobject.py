# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHManagedObject datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.sa.models.managedobject import ManagedObject


class CHManagedObjectDataSource(BaseDataSource):
    name = "ch_managedobject"

    def extract(self):
        r = []
        for mo in ManagedObject.objects.all().order_by("id"):
            r += [(
                mo.get_bi_id(),
                mo.id,
                mo.name,
                mo.address
            )]
        return r
