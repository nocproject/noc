# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.Platform tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.platform import Platform


class TestInvPlatform(BaseDocumentTest):
    model = Platform
