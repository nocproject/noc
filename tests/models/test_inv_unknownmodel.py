# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# inv.UnknownModel tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.inv.models.unknownmodel import UnknownModel


class TestInvUnknownModel(BaseDocumentTest):
    model = UnknownModel
