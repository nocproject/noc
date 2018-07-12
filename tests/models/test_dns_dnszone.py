# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dns.DNSZone tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.dns.models.dnszone import DNSZone


class TestTestDnsDNSZone(BaseModelTest):
    model = DNSZone
