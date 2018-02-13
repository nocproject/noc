# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VRF, Prefix, Address .project field
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from south.db import db


class Migration(object):
    def migrate_project(self, table):
        r = db.execute("""
            SELECT COUNT(*)
            FROM %s
            WHERE project IS NOT NULL AND project != ''""" % table)[0][0]
        if r:
            # Create custom field
            db.execute("""
            INSERT INTO main_customfield("table", name, is_active,
                label, "type", max_length, is_indexed)
            VALUES(%s, 'project', TRUE, 'Project', 'str', 256, TRUE)
            """, [table])

            # Move data
            db.execute("""
                ALTER TABLE %s RENAME project TO cust_project
            """ % table)
        else:
            # Drop column
            db.drop_column(table, "project")

    def forwards(self):
        self.migrate_project("ip_vrf")
        self.migrate_project("ip_prefix")
        self.migrate_project("ip_address")

    def backwards(self):
        pass
