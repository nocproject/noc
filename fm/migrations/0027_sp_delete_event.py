# -*- coding: utf-8 -*-

from south.db import db
<<<<<<< HEAD


class Migration:

    def forwards(self):
        db.execute(SQL_PROC)

=======
from django.db import models
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute(SQL_PROC)
    
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD

    DELETE FROM fm_eventdata
    WHERE event_id=p_event_id;

    DELETE FROM fm_eventlog
    WHERE event_id=p_event_id;

=======
    
    DELETE FROM fm_eventdata
    WHERE event_id=p_event_id;
    
    DELETE FROM fm_eventlog
    WHERE event_id=p_event_id;
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    DELETE FROM fm_event
    WHERE id=p_event_id;
END;
$$ LANGUAGE plpgsql;
<<<<<<< HEAD
"""
=======
"""
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
