# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.ObjectLog tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.objectlog import ObjectLog


class TestInvObjectLog(BaseDocumentTest):
    model = ObjectLog
