# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.MACDB tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.macdb import MACDB


class TestInvMACDB(BaseDocumentTest):
    model = MACDB
