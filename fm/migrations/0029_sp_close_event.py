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
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    IF p_status = 'C' THEN
        RETURN;
    END IF;

    UPDATE fm_event
    SET status='C'
    WHERE id=p_event_id;
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    INSERT INTO fm_eventlog(event_id,timestamp,from_status,to_status,message)
    VALUES(p_event_id,'now',p_status,'C',p_message);
END;
$$ LANGUAGE plpgsql;
<<<<<<< HEAD
"""
=======
"""
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
