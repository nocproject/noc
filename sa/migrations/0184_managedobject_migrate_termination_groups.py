# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Migrate ManagedObject Termination Groups to Resource Groups
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from south.db import db
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        tg_ids = [
            x[0]
            for x in db.execute(
                "SELECT DISTINCT termination_group_id "
                "FROM sa_managedobject "
                "WHERE termination_group_id IS NOT NULL"
            )
        ]
        st_ids = [
            x[0]
            for x in db.execute(
                "SELECT DISTINCT service_terminator_id "
                "FROM sa_managedobject "
                "WHERE service_terminator_id IS NOT NULL"
            )
        ]
        if not tg_ids and not st_ids:
            return  # Nothing to migrate
        mdb = get_db()
        rg_map = dict(
            (x["_legacy_id"], str(x["_id"]))
            for x in mdb.resourcegroups.find({
                "_legacy_id": {
                    "$exists": True
                }
            }, {
                "_id": 1,
                "_legacy_id": 1
            })
        )
        # Append to resource groups AS clients
        for tg_id in tg_ids:
            db.execute(
                "UPDATE sa_managedobject "
                "SET "
                "  static_client_groups = array_cat(static_client_groups, ARRAY[%s]::CHAR(24)[]), "
                "  effective_client_groups = array_cat(effective_client_groups, ARRAY[%s]::CHAR(24)[]) "                
                "WHERE termination_group_id = %s",
                [rg_map[tg_id], rg_map[tg_id], tg_id]
            )
        # Append to resource groups AS services
        for tg_id in st_ids:
            db.execute(
                "UPDATE sa_managedobject "
                "SET "
                "  static_service_groups = array_cat(static_service_groups, ARRAY[%s]::CHAR(24)[]), "
                "  effective_service_groups = array_cat(effective_service_groups, ARRAY[%s]::CHAR(24)[]) "                
                "WHERE service_terminator_id = %s",
                [rg_map[tg_id], rg_map[tg_id], tg_id]
            )
        # Finally remove columns
        db.drop_column("sa_managedobject", "termination_group_id")
        db.drop_column("sa_managedobject", "service_terminator_id")

    def backwards(self):
        pass
