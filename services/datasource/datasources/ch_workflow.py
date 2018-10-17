# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHWorkflow datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from pymongo import ReadPreference
# NOC modules
from .base import BaseDataSource
from noc.wf.models.workflow import Workflow


class CHWorkflowDataSource(BaseDataSource):
    name = "ch_workflow"

    def extract(self):
        for a in Workflow.objects.filter(read_preference=ReadPreference.SECONDARY_PREFERRED).all().order_by("id"):
            yield (
                a.bi_id,
                a.id,
                a.name,
                int(a.is_active)
            )
