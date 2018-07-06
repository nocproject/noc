# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# fm.FailedEvent tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.fm.models.failedevent import FailedEvent


class TestFmFailedEvent(BaseDocumentTest):
    model = FailedEvent
