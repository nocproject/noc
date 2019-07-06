# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# managedobject address cust index
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        func = """create or replace function cast_test_to_inet(varchar) returns inet as $$
        declare
             i inet;
        begin
             i := $1::inet;
             return i;
             EXCEPTION WHEN invalid_text_representation then
                    return '0.0.0.0'::inet;
        end;
        $$ language plpgsql immutable strict"""

        # Check index exists
        i = self.db.execute(
            """SELECT * FROM pg_indexes
                          WHERE tablename='sa_managedobject' AND indexname='x_managedobject_addressprefix'"""
        )
        if i:
            self.db.execute("DROP INDEX %s" % "x_managedobject_addressprefix")

        self.db.execute(func)
        self.db.execute(
            "CREATE INDEX x_managedobject_addressprefix ON sa_managedobject (cast_test_to_inet(address))"
        )
