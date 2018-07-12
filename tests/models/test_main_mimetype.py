# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# main.MIMEType tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.main.models.mimetype import MIMEType


class TestTestMainMIMEType(BaseModelTest):
    model = MIMEType
