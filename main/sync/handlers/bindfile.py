# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BINDFileHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import operator
## NOC modules
from dns import DNSZoneSyncHandler
from noc.sa.interfaces.base import StringParameter
from noc.main.sync.kvstore import KeyValueStore
from noc.dns.utils.zonefile import ZoneFile


class BINDFileHandler(DNSZoneSyncHandler):
    config = {
        # Zones file directory
        # (Absolute)
        "root": StringParameter(),
        # Path to include directory
        # (Relative to bind's chroot)
        "inc_root": StringParameter(required=False),
        # Extra config for the zones in the include file
        "inc_extra_config": StringParameter(required=False),
        # Shell command to execute when new zone created
        "on_new_zone": StringParameter(required=False),
        # Shell command to execute when zone deleted
        "on_deleted_zone": StringParameter(required=False),
        # Shell command to execute when zone updated
        "on_updated_zone": StringParameter(required=False)
    }

    INCLUDE_NAME = "noc_zones.conf"

    def __init__(self, daemon, name):
        super(BINDFileHandler, self).__init__(daemon, name)
        self.root = None
        self.inc_root = None
        self.inc_extra_config = None
        self.on_new_zone = None
        self.on_deleted_zone = None
        self.on_updated_zone = None
        self.db = None
        self.db_path = None
        self.inc_path = None
        self.touch_includes = False

    def configure(self, root, inc_root, inc_extra_config = None,
                  on_new_zone=None, on_deleted_zone=None,
                  on_updated_zone=None, **kwargs):
        if not os.path.isdir(root):
            raise ValueError("'%s' is not a directory" % root)
        self.root = root
        self.inc_root = inc_root or root
        self.inc_extra_config = inc_extra_config or "#set inc_extra_config option to add your config here"
        self.on_new_zone = on_new_zone or None
        self.on_deleted_zone = on_deleted_zone or None
        self.on_updated_zone = on_updated_zone or None
        self.inc_path = os.path.join(self.root, self.INCLUDE_NAME)
        db_path = os.path.join(self.root, "zones.db")
        if db_path != self.db_path:
            self.db_path = os.path.join(self.root, "zones.db")
            self.db = KeyValueStore(self.db_path, indexes=["zone"],
                            fields=["zone", "serial"])

    def get_zone_path(self, zone):
        return os.path.join(self.root, zone)

    def get_zone_inc_path(self, zone):
        """
        Get relative zone file path for include file
        :param zone:
        :return:
        """
        if self.inc_root:
            return os.path.join(self.inc_root, zone)
        else:
            return self.get_zone_path(zone)

    def write_zone(self, zone, records):
        zp = self.get_zone_path(zone)
        zf = ZoneFile(zone, records).get_text()
        self.logger.debug("Writing zone %s to %s", zone, zp)
        with open(zp, "w") as f:
            f.write(zf)

    def rebuild_includes(self):
        self.logger.info("Rebuilding include file %s", self.inc_path)
        ifile = [
            "#",
            "# NOC provisioned zones",
            "# WARNING: This is auto-generated file",
            "# Do not edit manually",
            "#",
            ""
        ]
        for z in sorted(self.db.find(),
                        key=operator.itemgetter("zone")):
            zone = z["zone"]
            ifile += [
                "# %s [%s]" % (zone, z["uuid"]),
                "zone %s {" % zone,
                "    type master;",
                "    file \"%s\";" % self.get_zone_inc_path(zone),
                "    %s" % self.inc_extra_config,
                "};",
                ""
            ]
        ifile = "\n".join(ifile)
        with open(self.inc_path, "w") as f:
            f.write(ifile)

    def on_configuration_done(self):
        if self.touch_includes or not os.path.exists(self.inc_path):
            self.rebuild_includes()
            self.touch_includes = False
        super(BINDFileHandler, self).on_configuration_done()

    def update_zone(self, uuid, zone, serial, records):
        c = self.db.get(uuid=uuid)
        if c:
            if c["serial"] == serial:
                self.logger.debug("%s zone serial not changed. Skipping", zone)
                return
            self.logger.info("Updating zone %s (%s)", zone, serial)
            self.write_zone(zone, records)
            # Update database
            c["serial"] = serial
            self.db.put(**c)
            # Run on_updated_zone trigger
            if self.on_updated_zone:
                self.queue_command(self.on_updated_zone, once=True,
                                   zone=zone, uuid=uuid, serial=serial)
        else:
            self.logger.info("Creating zone %s (%s)", zone, serial)
            self.write_zone(zone, records)
            # Update database
            self.db.put(uuid, zone=zone, serial=serial)
            self.touch_includes = True
            # Run on_new_zone trigger
            if self.on_new_zone:
                self.queue_command(self.on_new_zone, once=True,
                                   zone=zone, uuid=uuid, serial=serial)

    def delete_zone(self, uuid):
        c = self.db.get(uuid=uuid)
        if not c:
            return
        self.logger.info("Deleting zone %s", c["zone"])
        path = self.get_zone_path(c["zone"])
        if os.path.exists(path):
            self.logger.debug("Deleting file %s", path)
            os.unlink(path)
        self.db.delete(uuid)
        self.touch_includes = True
        if self.on_deleted_zone:
            self.queue_command(self.on_deleted_zone, once=True,
                               zone=c["zone"], uuid=uuid,
                               serial=c["serial"])
