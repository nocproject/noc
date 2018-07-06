# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.SyncCache tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.main.models.synccache import SyncCache


class TestMainSyncCache(BaseDocumentTest):
    model = SyncCache
