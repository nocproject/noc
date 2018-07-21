# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.ConnectionRule tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.connectionrule import ConnectionRule


class TestInvConnectionRule(BaseDocumentTest):
    model = ConnectionRule
