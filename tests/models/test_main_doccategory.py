# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.DocCategory tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.main.models.doccategory import DocCategory


class TestMainDocCategory(BaseDocumentTest):
    model = DocCategory
