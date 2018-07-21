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
        for mo in ManagedObject.objects.all().order_by("id"):
            yield (
                mo.bi_id,
                mo.id,
                mo.name,
                mo.address,
                mo.profile.name if mo.profile else "",
                mo.platform.name if mo.platform else "",
                mo.version.version if mo.version else "",
                mo.remote_id if mo.remote_id else "",
                mo.remote_system.name if mo.remote_system else "",
                mo.administrative_domain.id,
                mo.administrative_domain.name
            )
