# ----------------------------------------------------------------------
# trigger
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        if self.db.execute("SELECT COUNT(*) FROM pg_language WHERE lanname='plpgsql'")[0][0] == 0:
            self.db.execute("CREATE LANGUAGE plpgsql")
        self.db.execute(CREATE_F)
        self.db.execute(CREATE_T)


CREATE_F = """
CREATE OR REPLACE
FUNCTION f_sa_task_insert()
RETURNS TRIGGER
AS $$
BEGIN
    NOTIFY sa_new_task;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
"""

CREATE_T = """
CREATE TRIGGER t_sa_task_insert
AFTER INSERT ON sa_task
FOR EACH STATEMENT EXECUTE PROCEDURE f_sa_task_insert();
"""
