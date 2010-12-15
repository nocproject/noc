# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.fm.models import *

class Migration:
    
    CREATE_CLASSIFY_EVENT="""
    CREATE OR REPLACE
    FUNCTION classify_event(INTEGER, INTEGER, INTEGER, INTEGER, CHAR, VARCHAR, TEXT, TEXT[][])
    RETURNS VOID
    AS
    $$
    DECLARE
        p_event_id ALIAS FOR $1;
        p_event_class_id    ALIAS FOR $2;
        p_event_category_id ALIAS FOR $3;
        p_event_priority_id ALIAS FOR $4;
        p_status            ALIAS FOR $5;
        p_subject           ALIAS FOR $6;
        p_body              ALIAS FOR $7;
        p_vars              ALIAS FOR $8;
    BEGIN
        UPDATE fm_event
        SET
            event_class_id=p_event_class_id,
            event_category_id=p_event_category_id,
            event_priority_id=p_event_priority_id,
            status=p_status,
            subject=p_subject,
            body=p_body
        WHERE
            id=p_event_id;

        DELETE FROM fm_eventdata
        WHERE   event_id=p_event_id
            AND type!='>';

        FOR i IN array_lower(p_vars,1) .. array_upper(p_vars,1) LOOP
            INSERT INTO fm_eventdata(event_id, type, key, value)
            VALUES(p_event_id, p_vars[i][1], p_vars[i][2], p_vars[i][3]);
        END LOOP;
    END
    $$ LANGUAGE plpgsql;
    """
    
    DROP_CLASSIFY_EVENT="DROP FUNCTION classify_event(INTEGER, INTEGER, INTEGER, INTEGER, CHAR, VARCHAR, TEXT, TEXT[][])"
    
    def forwards(self):
        db.execute(self.CREATE_CLASSIFY_EVENT)
    
    def backwards(self):
        db.execute(self.DROP_CLASSIFY_EVENT)
    
