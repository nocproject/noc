# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.ObjectFile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.objectfile import ObjectFile


class TestInvObjectFile(BaseDocumentTest):
    model = ObjectFile
