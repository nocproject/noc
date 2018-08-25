# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# kb.KBUserBookmark tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.kb.models.kbuserbookmark import KBUserBookmark


class TestTestKbKBUserBookmark(BaseModelTest):
    model = KBUserBookmark
