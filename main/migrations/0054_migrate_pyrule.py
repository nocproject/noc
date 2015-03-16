# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Migrate pyrules to handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## Third-party modules
from south.db import db


class Migration:
    PMAP = [
        ("drop_event", "IEventTrigger"),
        ("get_single_result", "IReduceTask"),
        ("matrix_report", "IReduceTask"),
        ("mrt_result", "IReduceTask"),
        ("open_event", "IEvent"),
        ("prefix_list_provisioning", "IReduceTask"),
        ("refresh_config", "IEventTrigger"),
        ("result_report", "IReduceTask"),
        ("vc_provisioning", "IReduceTask"),
        ("version_inventory", "IReduceTask")
    ]

    def forwards(self):
        for name, iface in self.PMAP:
            handler = "noc.solutions.noc.default.pyrules.%s.%s" % (
                name, name
            )
            if db.execute(
                "SELECT COUNT(*) FROM main_pyrule WHERE name = %s", [name]
            )[0][0]:
                # Pyrule exists, change handler
                db.execute("UPDATE main_pyrule SET handler=%s,\"text\"=NULL WHERE name=%s", [
                    handler, name
                ])
            else:
                # Create new pyrule
                db.execute("INSERT INTO main_pyrule(name, interface, handler, description) VALUES(%s, %s, %s, %s)", [
                    name, iface, handler, "%s solution" % handler
                ])

    def backwards(self):
        pass