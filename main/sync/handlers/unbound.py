# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## UnboundHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## NOC modules
from bindfile import BINDFileHandler


class UnboundHandler(BINDFileHandler):
    def write_zone(self, zone, records):
        zp = self.get_zone_path(zone)
        z = ["local-zone: %s static" % zone]
        for r in records:
            x = ["local-data:", r.fqdn]
            if r.ttl:
                x += [str(r.ttl)]  # Write ttl
            x += ["IN", r.type, r.content]
            z += [" ".join(x)]
        self.logger.debug("Writing zone %s to %s", zone, zp)
        with open(zp, "w") as f:
            f.write("\n".join(z))

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
                "include: %s" % self.get_zone_inc_path(zone)
            ]
        ifile = "\n".join(ifile)
        with open(self.inc_path, "w") as f:
            f.write(ifile)
