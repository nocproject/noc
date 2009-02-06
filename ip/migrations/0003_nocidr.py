# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from south.db import db
from noc.ip.models import *
from noc.lib.fields import CIDRField

class Migration:
    
    def forwards(self):
        db.delete_column("ip_ipv4block","prefix")
        db.add_column("ip_ipv4block","prefix",CIDRField("prefix",null=True))
        db.execute("UPDATE ip_ipv4block SET prefix=prefix_cidr")
        db.delete_column("ip_ipv4block","prefix_cidr")
        db.execute("ALTER TABLE ip_ipv4block ALTER prefix SET NOT NULL")
        db.execute("DROP TRIGGER t_ip_ipv4block_modify ON ip_ipv4block")
        db.execute("DROP FUNCTION f_trigger_ip_ipv4block()")
        db.delete_column("ip_ipv4blockaccess","prefix")
        db.add_column("ip_ipv4blockaccess","prefix",CIDRField("prefix",null=True))
        db.execute("UPDATE ip_ipv4blockaccess SET prefix=prefix_cidr")
        db.delete_column("ip_ipv4blockaccess","prefix_cidr")
        db.execute("ALTER TABLE ip_ipv4blockaccess ALTER prefix SET NOT NULL")
        db.execute("DROP TRIGGER t_ip_ipv4blockaccess_modify ON ip_ipv4blockaccess")
        db.execute("DROP FUNCTION f_trigger_ip_ipv4blockaccess()")
        db.execute(RAW_SQL)
    
    def backwards(self):
        "Write your backwards migration here"

RAW_SQL="""
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
    WHERE vrf_id=vrf AND prefix >> inner_block AND prefix << outer_block;

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
    WHERE  v.vrf_group_id=p_vrf_group_id AND prefix >> inner_block AND prefix << outer_block;

    RETURN c;
END;
$$ LANGUAGE plpgsql;
"""
