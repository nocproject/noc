# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.ModelConnectionsCache tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.objectmodel import ModelConnectionsCache


class TestInvModelConnectionsCache(BaseDocumentTest):
    model = ModelConnectionsCache
