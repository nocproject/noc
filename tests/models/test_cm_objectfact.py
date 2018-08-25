# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# cm.ObjectFact tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.cm.models.objectfact import ObjectFact


class TestCmObjectFact(BaseDocumentTest):
    model = ObjectFact
