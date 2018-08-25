# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  ???
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
import bson.int64
# Third-party modules
from south.db import db
from noc.lib.nosql import get_db
from noc.core.model.fields import DocumentReferenceField
# NOC modules
from noc.core.bi.decorator import bi_hash


class Migration:
    depends_on = [
        ("wf", "0001_default_wf")
    ]

    def forwards(self):
        mdb = get_db()
        # Get default prefix profile
        coll = mdb["prefixprofiles"]
        d = coll.find_one({"name": "default"})
        default_prefix_profile = d["_id"]
        #
        coll = mdb["vpnprofiles"]
        default_id = bson.ObjectId()
        wf = bson.ObjectId("5a01d980b6f529000100d37a")
        profiles = [{
            "_id": default_id,
            "name": "default VRF",
            "type": "vrf",
            "description": "Default VRF profile",
            "workflow": wf,
            "default_prefix_profile": default_prefix_profile,
            "bi_id": bson.int64.Int64(bi_hash(default_id))
        }]
        # Convert styles
        style_profiles = {
            None: default_id
        }
        for style_id, in db.execute("SELECT DISTINCT style_id FROM ip_vrf"):
            if not style_id:
                continue
            p_id = bson.ObjectId()
            p = {
                "_id": p_id,
                "name": "VRF Style %s" % style_id,
                "type": "vrf",
                "description": "Auto-converted for VRF style %s" % style_id,
                "workflow": wf,
                "style": style_id,
                "default_prefix_profile": default_prefix_profile,
                "bi_id": bson.int64.Int64(bi_hash(p_id))
            }
            style_profiles[style_id] = p_id
            profiles += [p]
        # Insert profiles to database
        coll.insert(profiles)
        # Create Prefix.profile field
        db.add_column(
            "ip_vrf",
            "profile",
            DocumentReferenceField(
                "vc.VPNProfile",
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
                "UPDATE ip_vrf SET profile = %%s WHERE %s" % cond,
                [str(style_profiles[style_id])]
            )
        # Make Prefix.profile not nullable
        db.execute("ALTER TABLE ip_vrf ALTER profile SET NOT NULL")
        # Drop Prefix.style
        db.drop_column("ip_vrf", "style_id")

    def backwards(self):
        pass
