# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Remove AffectedObjects, Migrage to ManadgedObjects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        db = self.mongo_db
        for ao in db.noc.affectedobjects.aggregate(
            [
                {
                    "$project": {"_id": 0, "maintenance": 1, "objects": "$affected_objects.object"},
                }
            ]
        ):
            m_id = ao["maintenance"]
            objects = tuple(ao["objects"])
            if ao["objects"] == []:
                db.noc.affectedobjects.remove({"maintenance": m_id})
                continue
            mai = db.noc.maintenance.find_one({"_id": m_id})
            if mai["stop"] < datetime.datetime.now():
                db.noc.affectedobjects.remove({"maintenance": m_id})
                continue
            SQL_ADD = """UPDATE sa_managedobject
                            SET affected_maintenances = jsonb_insert(affected_maintenances,
                            '{"%s"}', '{"start": "%s", "stop": "%s"}'::jsonb)
                            WHERE id IN %s;""" % (
                str(m_id),
                mai["start"],
                mai["stop"],
                "(%s)" % ", ".join(map(repr, objects)),
            )
            self.db.execute(SQL_ADD)
            db.noc.affectedobjects.remove({"maintenance": m_id})
