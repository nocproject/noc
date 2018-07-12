# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# support.Crashinfo tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.support.models.crashinfo import Crashinfo


class TestSupportCrashinfo(BaseDocumentTest):
    model = Crashinfo
