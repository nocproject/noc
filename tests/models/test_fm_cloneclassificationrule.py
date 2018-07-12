# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fm.CloneClassificationRule tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.fm.models.cloneclassificationrule import CloneClassificationRule


class TestFmCloneClassificationRule(BaseDocumentTest):
    model = CloneClassificationRule
