# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Create ResourceGroups from Termination Groups
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import bson
from south.db import db
from pymongo import InsertOne
# NOC modules
from noc.core.bi.decorator import bi_hash
from noc.lib.nosql import get_db


class Migration(object):
    depends_on = [
        ("inv", "0017_initial_technologies")
    ]

    def forwards(self):
        # Get existing termination groups
        tg_data = db.execute(
            "SELECT id, name, description, remote_system, remote_id, tags "
            "FROM sa_terminationgroup"
        )
        if not tg_data:
            return  # Nothing to convert
        bulk = []
        # Create root node for migrated termination groups
        root_id = bson.ObjectId()
        bulk += [InsertOne({
            "_id": root_id,
            "name": "Converted T.G.",
            "parent": None,
            "description": "Created from former termination groups",
            "technology": bson.ObjectId("5b6d6819d706360001a0b716"),  # Group
            "bi_id": bson.Int64(bi_hash(root_id))
        })]
        # Attach termination groups
        for id, name, description, remote_system, remote_id, tags in tg_data:
            new_id = bson.ObjectId()
            bulk += [InsertOne({
                "_id": new_id,
                "name": name,
                "parent": root_id,
                "description": description,
                # May be changed by phone migration
                "technology": bson.ObjectId("5b6d6be1d706360001f5c04e"),  # Network | IPoE Termination
                "remote_system": bson.ObjectId(remote_system) if remote_system else None,
                "remote_id": remote_id,
                "bi_id": bson.Int64(bi_hash(new_id)),
                "_legacy_id": id  # To be removed in future migrations
            })]
        # Apply groups
        get_db().resourcegroups.bulk_write(bulk)

    def backwards(self):
        pass
