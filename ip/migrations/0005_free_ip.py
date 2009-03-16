
from south.db import db
from noc.ip.models import *

class Migration:
    
    def forwards(self):
        db.execute(SQL)
    
    def backwards(self):
        db.execute("DROP FUNCTION free_ip(INTEGER,CIDR)")

SQL="""CREATE OR REPLACE
FUNCTION free_ip(INTEGER,CIDR)
RETURNS INET
AS
$$
DECLARE
    p_vrf_id ALIAS FOR $1;
    p_prefix ALIAS FOR $2;
    r        RECORD;
    prev_ip  INET;
BEGIN
    prev_ip=host(network(p_prefix))::inet;
    
    FOR r IN
        SELECT ip
        FROM ip_ipv4address
        WHERE vrf_id=p_vrf_id AND ip << p_prefix AND ip>prev_ip
        ORDER BY ip
    LOOP
        IF r.ip-prev_ip>1 THEN
            RETURN prev_ip+1;
        ELSE
            prev_ip:=r.ip;
        END IF;
    END LOOP;
    IF host(broadcast(p_prefix))::inet - prev_ip > 1 THEN
        RETURN prev_ip+1;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;
"""
