# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# gis.Address tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.gis.models.address import Address


class TestGisAddress(BaseDocumentTest):
    model = Address
