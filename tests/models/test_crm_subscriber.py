# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# crm.Subscriber tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.crm.models.subscriber import Subscriber


class TestCrmSubscriber(BaseDocumentTest):
    model = Subscriber
