# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RRCache model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC models
from dnszone import DNSZone
from noc.lib.nosql import (Document, StringField, IntField,
                           ForeignKeyField, DateTimeField)


class RRCache(Document):
    meta = {
        "collection": "noc.dns.rrcache",
        "allow_inheritance": False,
        "indexes": [("zone", "name", "type")]
    }

    zone = ForeignKeyField(DNSZone)
    name = StringField()  # FQDN, including zone
    type = StringField()
    content = StringField()
    ttl = IntField()
    prio = IntField(required=False)
    changed = DateTimeField()

    def __unicode__(self):
        return "%s: %s %s %s" % (self.zone.name, self.name,
                                 self.type, self.content)

    @classmethod
    def update_zone(cls, zone):
        """
        Update RR cache and fill changelog
        :param zone:
        :type zone: DNSZone
        :return:
        """
        now = datetime.datetime.now()
        records = set(zone.get_records())
        fcached = [(r.id, r.name, r.type, r.content, r.ttl, r.prio)
            for r in cls.objects.filter(zone=zone.id)]
        cached = set(x[1:] for x in fcached)
        lcached = dict((x[1:], x[0]) for x in fcached)
        added = records - cached
        removed = cached - records
        # Remove hanging records
        ids = [lcached[x] for x in removed]
        cls.objects.filter(id__in=ids).delete()
        # Add records
        for name, type, content, ttl, prio in added:
            cls(zone=zone, name=name, type=type, content=content,
                ttl=ttl, prio=prio, changed=now).save()
