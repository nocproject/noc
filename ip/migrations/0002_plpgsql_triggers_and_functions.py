# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.ip.models import *

class Migration:
    depends_on=(
        ("sa","0002_trigger"),
    )
    def forwards(self):
        if not self.has_column("ip_ipv4block","prefix_cidr"):
            db.execute("ALTER TABLE ip_ipv4block ADD prefix_cidr CIDR")
            db.execute("UPDATE ip_ipv4block SET prefix_cidr=prefix::cidr")
            db.execute("ALTER TABLE ip_ipv4block ALTER prefix_cidr SET NOT NULL")
            db.execute("CREATE INDEX x_ip_ipv4block_prefix_cidr ON ip_ipv4block(prefix_cidr)")
        if not self.has_column("ip_ipv4blockaccess","prefix_cidr"):
            db.execute("ALTER TABLE ip_ipv4blockaccess ADD prefix_cidr CIDR")
            db.execute("UPDATE ip_ipv4blockaccess SET prefix_cidr=prefix::cidr")
            db.execute("ALTER TABLE ip_ipv4blockaccess ALTER prefix_cidr SET NOT NULL")
        db.execute(RAW_SQL_CREATE)
        if not self.has_trigger("ip_ipv4block","t_ip_ipv4block_modify"):
            db.execute(t_ip_ipv4block_modify)
        if not self.has_trigger("ip_ipv4blockaccess","t_ip_ipv4blockaccess_modify"):
            db.execute(t_ip_ipv4blockaccess_modify)
        
    def backwards(self):
        db.execute(RAW_SQL_DROP)
        db.execute("ALTER TABLE ip_ipv4block DROP COLUMN prefix_cidr")
        db.execute("ALTER TABLE ip_ipv4blockaccess DROP COLUMN prefix_cidr")
        
    def has_column(self,table,name):
        return db.execute("SELECT COUNT(*)>0 FROM pg_attribute a JOIN pg_class p ON (p.oid=a.attrelid)"\
            +" WHERE p.relname='%s' AND a.attname='%s'"%(table,name))[0][0]
        
    def has_trigger(self,table,name):
        return db.execute("SELECT COUNT(*)>0 FROM pg_trigger t JOIN pg_class p ON (p.oid=t.tgrelid)"\
            +" WHERE p.relname='%s' AND t.tgname='%s'"%(table,name))[0][0]
        
RAW_SQL_CREATE="""
CREATE OR REPLACE
FUNCTION ip_ipv4_block_depth(INTEGER,CIDR,CIDR)
RETURNS INTEGER
AS $$
DECLARE
    vrf         ALIAS FOR $1;
    inner_block ALIAS FOR $2;
    outer_block ALIAS FOR $3;
    c   INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO   c
    FROM ip_ipv4block
    WHERE vrf_id=vrf AND prefix_cidr >> inner_block AND prefix_cidr << outer_block;

    RETURN c;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE
FUNCTION ip_ipv4_block_depth_in_vrf_group(INTEGER,CIDR,CIDR)
RETURNS INTEGER
AS $$
DECLARE
    p_vrf_group_id ALIAS FOR $1;
    inner_block    ALIAS FOR $2;
    outer_block    ALIAS FOR $3;
    c   INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO   c
    FROM   ip_ipv4block b JOIN ip_vrf v ON (b.vrf_id=v.id)
    WHERE  v.vrf_group_id=p_vrf_group_id AND prefix_cidr >> inner_block AND prefix_cidr << outer_block;

    RETURN c;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE
FUNCTION hostname(TEXT)
RETURNS TEXT
AS $$
SELECT SUBSTRING($1 from E'^[a-zA-Z0-9\\-]+');
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE
FUNCTION domainname(TEXT)
RETURNS TEXT
AS $$
SELECT SUBSTRING($1 from E'^[a-zA-Z0-9\\-]+\\.(.+)'); 
$$ LANGUAGE SQL IMMUTABLE;

CREATE OR REPLACE
FUNCTION f_trigger_ip_ipv4block()
RETURNS TRIGGER
AS $$
BEGIN
    NEW.prefix_cidr:=NEW.prefix;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE
FUNCTION f_trigger_ip_ipv4blockaccess()
RETURNS TRIGGER
AS $$
BEGIN
    NEW.prefix_cidr:=NEW.prefix;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;"""

t_ip_ipv4block_modify="""
CREATE TRIGGER t_ip_ipv4block_modify
BEFORE INSERT OR UPDATE ON ip_ipv4block
FOR EACH ROW EXECUTE PROCEDURE f_trigger_ip_ipv4block();
"""

t_ip_ipv4blockaccess_modify="""
CREATE TRIGGER t_ip_ipv4blockaccess_modify
BEFORE INSERT OR UPDATE ON ip_ipv4blockaccess
FOR EACH ROW EXECUTE PROCEDURE f_trigger_ip_ipv4blockaccess();
"""

RAW_SQL_DROP="""
DROP TRIGGER IF EXISTS t_ip_ipv4block_modify ON ip_ipv4block;
DROP TRIGGER IF EXISTS t_ip_ipv4blockaccess_modify ON ip_ipv4blockaccess;
DROP FUNCTION f_trigger_ip_ipv4block();
DROP FUNCTION f_trigger_ip_ipv4blockaccess();
DROP FUNCTION ip_ipv4_block_depth(INTEGER,CIDR,CIDR);
DROP FUNCTION ip_ipv4_block_depth_in_vrf_group(INTEGER,CIDR,CIDR);
DROP FUNCTION hostname(TEXT);
DROP FUNCTION domainname(TEXT);
"""
