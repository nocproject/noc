# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dns.DNSZone tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
import pytest
# NOC modules
from .base import BaseModelTest
from noc.dns.models.dnszone import DNSZone


class TestTestDnsDNSZone(BaseModelTest):
    model = DNSZone

    @pytest.mark.parametrize("zone,ztype", [
        ("example.com", "F"),
        ("z12.example.com", "F"),
        ("z21.example.com", "F"),
        ("z31.example.com", "F"),
        ("0.0.10.in-addr.arpa", "4"),
        ("1.0.10.in-addr.arpa", "4"),
        ("8.b.d.0.1.0.0.2.ip6.int", "6"),
        ("1.9.b.d.0.1.0.0.2.ip6.int", "6")
    ])
    def test_zone_type(self, zone, ztype):
        z = DNSZone.objects.get(name=zone)
        assert z
        assert z.type == ztype

    @pytest.mark.parametrize("zone,prefix", [
        ("0.0.10.in-addr.arpa", "10.0.0.0/24"),
        ("1.0.10.in-addr.arpa", "10.0.1.0/24"),
        ("8.b.d.0.1.0.0.2.ip6.int", "2001:db8::/32"),
        ("1.9.b.d.0.1.0.0.2.ip6.int", "2001:db9:1000::/36")
    ])
    def test_reverse_prefix(self, zone, prefix):
        z = DNSZone.objects.get(name=zone)
        assert z
        assert z.reverse_prefix == prefix

    def test_rpsl(self):
        pass
