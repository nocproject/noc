# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fm.Enumeration tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.fm.models.enumeration import Enumeration


class TestFmEnumeration(BaseDocumentTest):
    model = Enumeration
