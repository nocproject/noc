# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Prefix.profile
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
import bson
# Third-party modules
from south.db import db
from noc.lib.nosql import get_db
from noc.core.model.fields import DocumentReferenceField


class Migration:
    depends_on = [
        ("wf", "0001_default_wf")
    ]

    def forwards(self):
        coll = get_db()["prefixprofiles"]
        default_id = bson.ObjectId()
        wf = bson.ObjectId("5a01d980b6f529000100d37a")
        profiles = [{
            "_id": default_id,
            "name": "default",
            "description": "Default prefix profile",
            "workflow": wf
        }]
        # Convert styles
        style_profiles = {}
        for style_id, in db.execute("SELECT DISTINCT style_id FROM ip_prefix"):
            if not style_id:
                style_profiles[None] = default_id
                continue
            p_id = bson.ObjectId()
            p = {
                "_id": p_id,
                "name": "Style %s" % style_id,
                "description": "Auto-converted for style %s" % style_id,
                "workflow": wf,
                "style": style_id
            }
            style_profiles[style_id] = p_id
            profiles += [p]
        # Insert profiles to database
        coll.insert(profiles)
        # Create Prefix.profile field
        db.add_column(
            "ip_prefix",
            "profile",
            DocumentReferenceField(
                "ip.PrefixProfile",
                null=True, blank=True
            )
        )
        # Migrate profile styles
        for style_id in style_profiles:
            if style_id:
                cond = "style_id = %s" % style_id
            else:
                cond = "style_id IS NULL"
            db.execute(
                "UPDATE ip_prefix SET profile = %%s WHERE %s" % cond,
                [str(style_profiles[style_id])]
            )
        # Make Prefix.profile not nullable
        db.execute("ALTER TABLE ip_prefix ALTER profile SET NOT NULL")
        # Drop Prefix.style
        db.drop_column("ip_prefix", "style_id")

    def backwards(self):
        pass
