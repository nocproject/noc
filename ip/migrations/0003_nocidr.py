# ----------------------------------------------------------------------
# nocidr
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.model.fields import CIDRField
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        self.db.delete_column("ip_ipv4block", "prefix")
        self.db.add_column("ip_ipv4block", "prefix", CIDRField("prefix", null=True))
        self.db.execute("UPDATE ip_ipv4block SET prefix=prefix_cidr")
        self.db.delete_column("ip_ipv4block", "prefix_cidr")
        self.db.execute("ALTER TABLE ip_ipv4block ALTER prefix SET NOT NULL")
        self.db.execute("DROP TRIGGER t_ip_ipv4block_modify ON ip_ipv4block")
        self.db.execute("DROP FUNCTION f_trigger_ip_ipv4block()")
        self.db.delete_column("ip_ipv4blockaccess", "prefix")
        self.db.add_column("ip_ipv4blockaccess", "prefix", CIDRField("prefix", null=True))
        self.db.execute("UPDATE ip_ipv4blockaccess SET prefix=prefix_cidr")
        self.db.delete_column("ip_ipv4blockaccess", "prefix_cidr")
        self.db.execute("ALTER TABLE ip_ipv4blockaccess ALTER prefix SET NOT NULL")
        self.db.execute("DROP TRIGGER t_ip_ipv4blockaccess_modify ON ip_ipv4blockaccess")
        self.db.execute("DROP FUNCTION f_trigger_ip_ipv4blockaccess()")
        self.db.execute(RAW_SQL)


RAW_SQL = """
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
