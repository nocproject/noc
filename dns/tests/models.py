# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unittests for access system
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from unittest import TestCase
from noc.dns.models import *
from noc.ip.models import VRF, Address
##
##
##
class AccessTestCase(TestCase):
    ADDRESSES = [("h1.example.com", "10.0.0.3"),
                 ("h2.example.com", "10.0.0.4"),
                 ("h3.example.com", "10.0.1.3"),
                 ("h4.example.com", "2001:db8::1"),
                 ("h5.example.com", "2001:db8::2")]
    ##
    ## Create default data set
    ##
    def setUp(self):
        # NS1
        self.ns1 = DNSServer(name="ns1.example.com", ip="10.0.0.1")
        self.ns1.save()
        # NS2
        self.ns2 = DNSServer(name="ns2.example.com",
                    ip="10.0.0.2", location="Mordor")
        self.ns2.save()
        # P1
        self.profile1 = DNSZoneProfile(name="p1", zone_soa="example.com",
            zone_contact="dns@example.com")
        self.profile1.save()
        self.profile1.masters.add(self.ns1)
        self.profile1.masters.add(self.ns2)
        # P2
        self.profile2 = DNSZoneProfile(name="p2", zone_soa="example.com",
            zone_contact="dns@example.com")
        self.profile2.save()
        self.profile2.masters.add(self.ns1)
        self.profile2.slaves.add(self.ns2)
        # P3
        self.profile3 = DNSZoneProfile(name="p3", zone_soa="example.com",
            zone_contact="dns@example.com")
        self.profile3.save()
        self.profile3.masters.add(self.ns1)
        # Z11
        self.z11 = DNSZone(name="example.com", is_auto_generated=True,
            profile=self.profile1)
        self.z11.save()
        # Z12
        self.z12 = DNSZone(name="z12.example.com", is_auto_generated=True,
            profile=self.profile1)
        self.z12.save()
        # Z21
        self.z21 = DNSZone(name="z21.example.com", is_auto_generated=True,
            profile=self.profile2)
        self.z21.save()
        # Z31
        self.z31 = DNSZone(name="z31.example.com", is_auto_generated=True,
            profile=self.profile3)
        self.z31.save()
        # ZR41
        self.zr41 = DNSZone(name="0.0.10.in-addr.arpa", is_auto_generated=True,
            profile=self.profile1)
        self.zr41.save()
        DNSZoneRecord(zone=self.zr41, name="8/29", type="NS",
            content="ns3.example.com").save()
        # ZR42
        self.zr42 = DNSZone(name="1.0.10.in-addr.arpa", is_auto_generated=True,
            profile=self.profile1)
        self.zr42.save()
        # ZR61
        self.zr61 = DNSZone(name="8.b.d.0.1.0.0.2.ip6.int",
            is_auto_generated=True,
            profile=self.profile1)
        self.zr61.save()
        # ZR62
        self.zr62 = DNSZone(name="1.9.b.d.0.1.0.0.2.ip6.int",
            is_auto_generated=True,
            profile=self.profile1)
        self.zr62.save()
        #
        vrf = VRF.get_global()
        # Save IPv6 status
        self.has_ipv6 = vrf.afi_ipv6
        if not self.has_ipv6:
            vrf.afi_ipv6 = True
            vrf.save()
        # Add addressess
        for h, a in self.ADDRESSES:
            Address(vrf=vrf, address=a, fqdn=h).save()
    
    ##
    ## Cleanup
    ##
    def tearDown(self):
        self.z11.delete()
        del self.z11
        self.z12.delete()
        del self.z12
        self.z21.delete()
        del self.z21
        self.z31.delete()
        del self.z31
        self.zr41.dnszonerecord_set.all().delete()
        self.zr41.delete()
        del self.zr41
        self.zr42.delete()
        del self.zr42
        self.zr61.delete()
        del self.zr61
        self.zr62.delete()
        del self.zr62
        self.profile1.delete()
        del self.profile1
        self.profile2.delete()
        del self.profile2
        self.profile3.delete()
        del self.profile3
        self.ns1.delete()
        del self.ns1
        self.ns2.delete()
        del self.ns2
        vrf = VRF.get_global()
        for h, a in self.ADDRESSES:
            Address.objects.get(vrf=vrf, address=a, fqdn=h).delete()
        if not self.has_ipv6:
            vrf.afi_ipv6 = False
            vrf.save()
    
    ##
    ## Test __unicode__ methods
    ##
    def test_unicode(self):
        for c in [DNSServer, DNSZoneProfile, DNSZone, DNSZoneRecord]:
            for o in c.objects.all():
                unicode(o)
    
    ##
    ## Test .get_absolute_url methods
    ##
    def test_absolute_url(self):
        for c in [DNSServer, DNSZoneProfile, DNSZone]:
            if hasattr(c, "get_absolute_url"):
                for o in c.objects.all():
                    url = o.get_absolute_url()
                    self.assertTrue(str(o.id) in url,
                        "%s not in %s" % (o.id, url))
    
    ##
    ## Test DNSServer.expand_vars()
    ##
    def test_dnsserver_expand_vars(self):
        s = "TEST: %(ip)s - %(ns)s"
        self.assertEqual(self.ns1.expand_vars(s),
            "TEST: 10.0.0.1 - ns1.example.com")
        self.assertEqual(self.ns2.expand_vars(s),
            "TEST: 10.0.0.2 - ns2.example.com")
    
    ##
    ## Test DNSServer.generator_class
    ##
    def test_dnsserver_generator_class(self):
        self.assertEqual(self.ns1.generator_class.name, "BINDv9")
        self.assertEqual(self.ns2.generator_class.name, "BINDv9")
    
    ##
    ## Test DNSZoneProfile.authoritative_servers
    ##
    def test_profile_authoritative_servers(self):
        # Check profile 1
        self.assertTrue(self.ns1 in self.profile1.authoritative_servers)
        self.assertTrue(self.ns2 in self.profile1.authoritative_servers)
        # Check profile 2
        self.assertTrue(self.ns1 in self.profile2.authoritative_servers)
        self.assertTrue(self.ns2 in self.profile2.authoritative_servers)
        # Check profile 3
        self.assertTrue(self.ns1 in self.profile3.authoritative_servers)
        self.assertFalse(self.ns2 in self.profile3.authoritative_servers)
    
    ##
    ## Test DNSZone managers
    ##
    def test_zone_managers(self):
        fz = list(DNSZone.forward_zones.all())
        rz = list(DNSZone.reverse_zones.all())
        for z in [self.z11, self.z12, self.z21, self.z31]:
            self.assertTrue(z in fz)
            self.assertFalse(z in rz)
        for z in [self.zr41, self.zr42, self.zr61, self.zr62]:
            self.assertTrue(z in rz)
            self.assertFalse(z in fz)
    
    ##
    ## Test DNSZone.type
    ##
    def test_zone_type(self):
        for fz in [self.z11, self.z12, self.z21, self.z31]:
            self.assertEqual(fz.type, "F")
        for r4z in [self.zr41, self.zr42]:
            self.assertEqual(r4z.type, "R4")
        for r6z in [self.zr61, self.zr62]:
            self.assertEqual(r6z.type, "R6")
    
    ##
    ## Test DNSZone.reverse_prefix
    ##
    def test_zone_reverse_prefix(self):
        self.assertEqual(self.zr41.reverse_prefix, "10.0.0.0/24")
        self.assertEqual(self.zr42.reverse_prefix, "10.0.1.0/24")
        self.assertEqual(self.zr61.reverse_prefix, "2001:db8::/32")
        self.assertEqual(self.zr62.reverse_prefix, "2001:db9:1000::/36")
    
    ##
    ## DNSZone.next_serial
    ##
    def test_zone_next_serial(self):
        for z in DNSZone.objects.all():
            s = z.next_serial
            self.assertEqual(s % 100, 0)
            z.serial = z.next_serial
            z.save()
            s = z.next_serial
            self.assertEqual(s % 100, 1)
    
    ##
    ##
    ##
    def test_zone_records(self):
        z11_records = self.z11.records
        for r in [("ns1", "A", "10.0.0.1"),
                  ("ns2", "A", "10.0.0.2"),
                  ("z12", "NS", "ns1.example.com."),
                  ("z12", "NS", "ns2.example.com."),
                  ("z21", "NS", "ns1.example.com."),
                  ("z21", "NS", "ns2.example.com."),
                  ("z31", "NS", "ns1.example.com.")]:
            self.assertTrue(r in z11_records)
        zr41_records = self.zr41.records
        # Check classless delegation
        for r in [
                ("8", "CNAME", "8.8/29"),
                ("9", "CNAME", "9.8/29"),
                ("10", "CNAME", "10.8/29"),
                ("11", "CNAME", "11.8/29"),
                ("12", "CNAME", "12.8/29"),
                ("13", "CNAME", "13.8/29"),
                ("14", "CNAME", "14.8/29"),
                ("15", "CNAME", "15.8/29"),
                ("8/29", "NS", "ns3.example.com")]:
            self.assertTrue(r in zr41_records,
                "%s not in %s" % (r, zr41_records))
        zr42_records = self.zr42.records
        zr61_records = self.zr61.records
    
    ##
    ##
    ##
    def test_zone_rpsl(self):
        for z in DNSZone.objects.all():
            rpsl = z.rpsl
            if z.type == "F":
                self.assertEqual(rpsl, "")
    
