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
        c_ids = [
            x[0]
            for x in db.execute(
                "SELECT DISTINCT filter_termination_group_id "
                "FROM sa_managedobjectselector "
                "WHERE filter_termination_group_id IS NOT NULL"
            )
        ]
        s_ids = [
            x[0]
            for x in db.execute(
                "SELECT DISTINCT filter_service_terminator_id "
                "FROM sa_managedobjectselector "
                "WHERE filter_service_terminator_id IS NOT NULL"
            )
        ]
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
        for tg_id in c_ids:
            db.execute(
                "UPDATE sa_managedobjectselector "
                "SET "
                "  filter_client_group = %s "
                "WHERE filter_termination_group_id = %s",
                [rg_map[tg_id], tg_id]
            )
        # Append to resource groups AS services
        for tg_id in s_ids:
            db.execute(
                "UPDATE sa_managedobjectselector "
                "SET "
                "  filter_service_group = %s "
                "WHERE filter_service_terminator_id = %s",
                [rg_map[tg_id], tg_id]
            )
        # Finally remove columns
        db.drop_column("sa_managedobjectselector", "filter_termination_group_id")
        db.drop_column("sa_managedobjectselector", "filter_service_terminator_id")

    def backwards(self):
        pass
