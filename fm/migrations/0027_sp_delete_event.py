# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute(SQL_PROC)
    
    
    def backwards(self):
        pass

SQL_PROC="""
CREATE OR REPLACE
FUNCTION delete_event(INTEGER)
RETURNS VOID
AS
$$
DECLARE
    p_event_id ALIAS FOR $1;
BEGIN
    DELETE FROM fm_eventrepeat
    WHERE event_id=p_event_id;
    
    DELETE FROM fm_eventdata
    WHERE event_id=p_event_id;
    
    DELETE FROM fm_eventlog
    WHERE event_id=p_event_id;
    
    DELETE FROM fm_event
    WHERE id=p_event_id;
END;
$$ LANGUAGE plpgsql;
"""