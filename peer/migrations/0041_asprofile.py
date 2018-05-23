# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ASProfile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
import bson
# NOC module
from noc.lib.nosql import get_db
from noc.core.model.fields import DocumentReferenceField


class Migration(object):
    def forwards(self):
        # Create default profile
        P_ID = "5ae04bcb45ce8300f385edb2"
        pcoll = get_db()["asprofiles"]
        pcoll.insert({
            "_id": bson.ObjectId(P_ID),
            "name": "default",
            "description": "Default Profile"
        })
        # Create AS.profile
        db.add_column(
            "peer_as",
            "profile",
            DocumentReferenceField("peer.ASProfile", null=True, blank=True)
        )
        # Update profiles
        db.execute("UPDATE peer_as SET profile = %s", [P_ID])
        # Set profile not null
        db.execute("ALTER TABLE peer_as ALTER profile SET NOT NULL")

    def backwards(self):
        pass
