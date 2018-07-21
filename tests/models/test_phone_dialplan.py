# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# phone.DialPlan tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.phone.models.dialplan import DialPlan


class TestPhoneDialPlan(BaseDocumentTest):
    model = DialPlan
