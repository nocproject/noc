# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dns.DNSZoneRecord tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.dns.models.dnszonerecord import DNSZoneRecord


class TestTestDnsDNSZoneRecord(BaseModelTest):
    model = DNSZoneRecord
