# ----------------------------------------------------------------------
# lg query default data
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.migration.base import BaseMigration

# Values:
#   (QueryType,Command,ArgRequired)
DEFAULT = {
    "Cisco.IOS": [
        ("ipv4:bgp", "show ip bgp %(query)s"),
        ("advertised-routes", "show ip bgp neighbors %(query)s advertised-routes"),
        ("summary", "show ip bgp summary"),
        ("ping", "ping %(query)s"),
        ("trace", "traceroute %(query)s"),
    ],
    "Juniper.JUNOS": [
        ("ipv4:bgp", "show route table inet.0 %(query)s detail"),
        ("advertised-routes", "show route advertising-protocol bgp %(query)s %(query)s"),
        ("summary", "show bgp summary"),
        ("ping", "ping count 5 %(query)s"),
        ("trace", "traceroute %(query)s as-number-lookup"),
    ],
}


class Migration(BaseMigration):
    def migrate(self):
        qtype = {}
        for ppt in DEFAULT:
            if (
                self.db.execute("SELECT COUNT(*) FROM peer_peeringpointtype WHERE name=%s", [ppt])[
                    0
                ][0]
                == 0
            ):
                self.db.execute("INSERT INTO peer_peeringpointtype(name) VALUES(%s)", [ppt])
            ppt_id = self.db.execute("SELECT id FROM peer_peeringpointtype WHERE name=%s", [ppt])[
                0
            ][0]
            for k, v in DEFAULT[ppt]:
                if k not in qtype:
                    self.db.execute("INSERT INTO peer_lgquerytype(name) VALUES(%s)", [k])
                    qtype[k] = self.db.execute(
                        "SELECT id FROM peer_lgquerytype WHERE name=%s", [k]
                    )[0][0]
                q = qtype[k]
                if (
                    self.db.execute(
                        """SELECT COUNT(*) FROM peer_lgquerycommand
                                WHERE peering_point_type_id=%s
                                AND query_type_id=%s""",
                        [ppt_id, q],
                    )[0][0]
                    == 0
                ):
                    self.db.execute(
                        """INSERT INTO peer_lgquerycommand(peering_point_type_id,query_type_id,command)
                        VALUES(%s,%s,%s)""",
                        [ppt_id, q, v],
                    )
