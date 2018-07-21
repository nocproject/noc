# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.Object tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.object import Object


class TestInvObject(BaseDocumentTest):
    model = Object
