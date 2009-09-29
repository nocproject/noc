# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute(SQL_PROC)
    
    
    def backwards(self):
        db.execute("DROP FUNCTION close_event(INTEGER,TEXT)")

SQL_PROC="""
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