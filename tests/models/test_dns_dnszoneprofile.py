# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# dns.DNSZoneProfile tests
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
from noc.dns.models.dnszoneprofile import DNSZoneProfile
from noc.dns.models.dnsserver import DNSServer


class TestTestDnsDNSZoneProfile(BaseModelTest):
    model = DNSZoneProfile

    @pytest.mark.parametrize("zoneprofile,dns_server,is_authoritative", [
        ("p1", "ns1.example.com", True),
        ("p1", "ns2.example.com", True),
        ("p2", "ns1.example.com", True),
        ("p2", "ns2.example.com", True),
        ("p3", "ns1.example.com", True),
        ("p3", "ns2.example.com", False),
    ])
    def test_autoritative_servers(self, zoneprofile, dns_server, is_authoritative):
        zp = DNSZoneProfile.objects.get(name=zoneprofile)
        assert zp
        ns = DNSServer.objects.get(name=dns_server)
        assert ns
        assert (ns in zp.authoritative_servers) is is_authoritative
