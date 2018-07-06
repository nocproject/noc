# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ip.AddressProfile tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDocumentTest
from noc.ip.models.addressprofile import AddressProfile


class TestIpAddressProfile(BaseDocumentTest):
    model = AddressProfile
