# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Create "default" interface profie
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.lib.nosql import get_db

DEFAULT_NAME = "default"

class Migration:
    def forwards(self):
        c = get_db().noc.interface_profiles
        if not c.find({"name": DEFAULT_NAME}).count():
            c.insert({
                "name": DEFAULT_NAME,
                "description": "Fallback interface profile.\n"
                               "Do not remove or rename",
                "link_events": "A"
            })

    def backwards(self):
        pass
