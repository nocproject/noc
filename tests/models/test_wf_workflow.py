# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# wf.Workflow tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.wf.models.workflow import Workflow


class TestWfWorkflow(BaseDocumentTest):
    model = Workflow
