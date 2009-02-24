
from south.db import db
from noc.fm.models import *

class Migration:
    
    def forwards(self):
        db.execute(PROC)
    
    def backwards(self):
        pass

PROC="""
CREATE OR REPLACE
FUNCTION update_event_classification(INTEGER,INTEGER,INTEGER,INTEGER,TEXT,TEXT,TEXT[][])
RETURNS VOID
AS
$$
DECLARE
    p_event_id          ALIAS FOR $1;
    p_event_class_id    ALIAS FOR $2;
    p_event_category_id ALIAS FOR $3; 
    p_event_priority_id ALIAS FOR $4;
    p_subject           ALIAS FOR $5;
    p_body              ALIAS FOR $6;
    p_vars              ALIAS FOR $7;
BEGIN
    DELETE FROM fm_eventdata
    WHERE event_id=p_event_id
        AND "type" IN ('R','V');
    
    FOR i IN array_lower(p_vars,1) .. array_upper(p_vars,1) LOOP
        INSERT INTO fm_eventdata(event_id,"type",key,value)
        VALUES(p_event_id,p_vars[i][1],p_vars[i][2],p_vars[i][3]);
    END LOOP;
    
    UPDATE fm_event
    SET
        event_class_id=p_event_class_id,
        event_category_id=p_event_category_id,
        event_priority_id=p_event_priority_id,
        status='A',
        subject=p_subject,
        body=p_body
    WHERE id=p_event_id;
END;
$$ LANGUAGE plpgsql;
"""