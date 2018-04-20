# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NSDHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator
## NOC modules
from bindfile import BINDFileHandler


class NSDHandler(BINDFileHandler):
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
                "zone:",
                "    name: %s" % zone,
                "    zonefile: %s" % self.get_zone_inc_path(zone),
                ""
            ]
        ifile = "\n".join(ifile)
        with open(self.inc_path, "w") as f:
            f.write(ifile)
