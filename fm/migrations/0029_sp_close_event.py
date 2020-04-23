# ----------------------------------------------------------------------
# sp close event
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.execute(SQL_PROC)


SQL_PROC = """
CREATE OR REPLACE
FUNCTION close_event(INTEGER,TEXT)
RETURNS VOID
AS
$$
DECLARE
    p_event_id ALIAS FOR $1;
    p_message  ALIAS FOR $2;
    p_status   TEXT;
BEGIN
    SELECT status
    INTO   p_status
    FROM   fm_event
    WHERE  id=p_event_id;

    IF p_status = 'C' THEN
        RETURN;
    END IF;

    UPDATE fm_event
    SET status='C'
    WHERE id=p_event_id;

    INSERT INTO fm_eventlog(event_id,timestamp,from_status,to_status,message)
    VALUES(p_event_id,'now',p_status,'C',p_message);
END;
$$ LANGUAGE plpgsql;
"""
