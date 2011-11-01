# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZoneRecordType model test
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.lib.test import ModelTestCase
from noc.dns.models import DNSZoneRecordType


class DNSZoneRecordTypeModelTestCase(ModelTestCase):
    model = DNSZoneRecordType

    data = [
        {"type": "ZT_ALL", "is_active": True, "validation": ""},
        {"type": "ZT_IPv4", "is_active": True, "validation": "^t: IPv4$"},
        {"type": "ZT_FQDN", "is_active": True, "validation": "^t: FQDN$"}
    ]

    test_values = {
        "foobar": ["ZT_ALL"],
        "10.10.10.10": ["ZT_ALL"],
        "t: 10.10.10.10": ["ZT_ALL", "ZT_IPv4", "ZT_FQDN"],
        "t: example.com": ["ZT_ALL", "ZT_FQDN"]
    }

    def object_test(self, obj):
        for t in self.test_values:
            r = obj.is_valid(t)
            if obj.type in self.test_values[t]:
                self.assertTrue(r, "%s.is_valid('%s')" % (obj.type, t))
            else:
                self.assertFalse(r, "%s.is_valid('%s')" % (obj.type, t))

    def test_save(self):
        """
        Check exception on invalid regular expression risen
        """
        t = DNSZoneRecordType(type="ZT_RE_FAIL", is_active=True,
                              validation="+")
        with self.assertRaises(ValueError):
            t.save()

    def test_migrations(self):
        """
        Check default RR types created during migration
        """
        self.assertEquals(DNSZoneRecordType.objects.count(), 33)
        self.assertEquals(DNSZoneRecordType.objects.filter(is_active=True).count(), 10)
        self.assertEquals(DNSZoneRecordType.objects.filter(is_active=False).count(), 23)
