# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# trigger
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Third-party modules
from south.db import db


class Migration(object):
    def forwards(self):
        if db.execute("SELECT COUNT(*) FROM pg_language WHERE lanname='plpgsql'")[0][0] == 0:
            db.execute("CREATE LANGUAGE plpgsql")
        db.execute(CREATE_F)
        db.execute(CREATE_T)

    def backwards(self):
        db.execute(DROP_T)
        db.execute(DROP_F)


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

DROP_T = """
DROP TRIGGER IF EXISTS t_sa_task_insert ON sa_task;
"""

DROP_F = """
DROP FUNCTION f_sa_task_insert();
"""
