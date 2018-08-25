# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dns.DNSServer tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.dns.models.dnsserver import DNSServer


class TestTestDnsDNSServer(BaseModelTest):
    model = DNSServer
