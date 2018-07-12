# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.SubInterface tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.subinterface import SubInterface


class TestInvSubInterface(BaseDocumentTest):
    model = SubInterface
