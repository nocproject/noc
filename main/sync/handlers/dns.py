# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZoneSyncHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from base import SyncHandler
from noc.dns.utils.zonefile import RR


class DNSZoneSyncHandler(SyncHandler):
    type = "dns.DNSZone"
    RR = RR

    def check_data(self, data):
        records = data.get("records", [])
        if not records:
            self.logger.error("Zone must contain SOA record at least")
            return False
        soa = RR(*records[0])
        if soa.type != "SOA":
            self.logger.error("First record must be SOA")
            return False
        return True

    def on_create(self, uuid, data):
        """
        Object first seen
        """
        if not self.check_data(data):
            return
        records = [RR(*r) for r in data["records"]]
        soa = records[0]
        serial = soa.content.split()[2]
        self.update_zone(uuid, soa.fqdn[:-1], serial, records)

    def on_delete(self, uuid):
        """
        Object removed
        """
        self.delete_zone(uuid)

    def on_change(self, uuid, data):
        """
        Object changed
        """
        return self.on_create(uuid, data)

    def update_zone(self, uuid, zone, serial, records):
        pass

    def delete_zone(self, uuid):
        pass
