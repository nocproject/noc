# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# sa.Action tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.sa.models.action import Action


class TestSaAction(BaseDocumentTest):
    model = Action
