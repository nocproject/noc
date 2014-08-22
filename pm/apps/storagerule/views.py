# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.storagerule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.storagerule import StorageRule


class StorageRuleApplication(ExtDocApplication):
    """
    StorageRule application
    """
    title = "Storage Rule"
    menu = "Setup | Storage Rules"
    model = StorageRule
    query_fields = ["name", "description"]

    def field_retention_text(self, o):
        r = ["every %s%s for %s%s" % (
            r.precision, r.precision_unit, r.duration, r.duration_unit
        ) for r in o.retentions]
        return ", ".join(r)

    def field_interval(self, o):
        return o.get_interval()
