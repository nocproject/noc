# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHState datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.wf.models.state import State


class CHStateDataSource(BaseDataSource):
    name = "ch_state"

    def extract(self):
        for a in State.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED).all().order_by("id"):
            yield (
                a.bi_id,
                a.id,
                a.name,
                a.workflow.name,
                int(a.is_default),
                int(a.is_productive)
            )
