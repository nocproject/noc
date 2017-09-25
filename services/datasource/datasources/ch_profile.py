# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHProfile datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.sa.models.profile import Profile


class CHProfileClassDataSource(BaseDataSource):
    name = "ch_profile"

    def extract(self):
        for a in Profile.objects.all().order_by("id"):
            yield (
                a.get_bi_id(),
                a.id,
                a.name
            )
