# encoding: utf-8

# Third-party modules
from south.db import db


class Migration(object):
    GET_PARENT_SQL = """
        SELECT id
        FROM   ip_prefix
        WHERE
                vrf_id=$1
            AND afi='4'
            AND prefix >> $2
        ORDER BY masklen(prefix) DESC
        LIMIT 1
    """

    def forwards(self):
        # VRF Group
        db.execute("UPDATE ip_vrfgroup SET address_constraint='G' WHERE unique_addresses=TRUE")
        # IPv4 Block
        # @todo: migrate tags
        for id, vrf_id, asn_id, prefix, vc_id, description, tt, tags in db.execute(
            """
            SELECT id,vrf_id,asn_id,prefix,vc_id,description,tt,tags
            FROM ip_ipv4block
            ORDER BY prefix
            """
        ):
            if prefix == "0.0.0.0/0":
                parent_id = None
            else:
                parent_id = db.execute(self.GET_PARENT_SQL, [vrf_id, prefix])[0][0]
            db.execute(
                """
                INSERT INTO ip_prefix(parent_id,vrf_id,afi,prefix,asn_id,vc_id,description,tags,tt)
                VALUES(%s,%s,'4',%s,%s,%s,%s,%s,%s)
                """,
                [parent_id, vrf_id, prefix, asn_id, vc_id, description, tags, tt]
            )
        # IPv4 Address
        # @todo: migrate tags
        for id, vrf_id, fqdn, ip, description, tt, tags, managed_object_id, auto_update_mac, mac in db.execute(
            """
            SELECT id,vrf_id,fqdn,ip,description,tt,tags,managed_object_id,auto_update_mac,mac
            FROM ip_ipv4address
            ORDER BY ip
            """
        ):
            prefix_id = db.execute(self.GET_PARENT_SQL, [vrf_id, ip])[0][0]
            db.execute(
                """
                INSERT INTO ip_address(prefix_id,vrf_id,afi,address,fqdn,mac,auto_update_mac,managed_object_id,description,tags,tt)
                VALUES(%s,%s,'4',%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                [prefix_id, vrf_id, ip, fqdn, mac, auto_update_mac, managed_object_id, description, tags, tt]
            )
        # PrefixAccess
        db.execute(
            """
            INSERT INTO ip_prefixaccess(user_id,vrf_id,afi,prefix,can_view,can_change)
            SELECT user_id,vrf_id,'4',prefix,TRUE,TRUE
            FROM ip_ipv4blockaccess
            """
        )
        # Prefix bookmark
        for user_id, vrf_id, prefix in db.execute(
            """
            SELECT b.user_id,p.vrf_id,p.prefix
            FROM ip_ipv4blockbookmark b JOIN ip_ipv4block p ON b.prefix_id=p.id
            """
        ):
            prefix_id = db.execute(
                """
                SELECT id
                FROM ip_prefix
                WHERE
                  vrf_id=%s
                  AND prefix=%s
                  AND afi='4'
                """,
                [vrf_id, prefix]
            )[0][0]
            db.execute("INSERT INTO ip_prefixbookmark(user_id,prefix_id) VALUES(%s,%s)", [user_id, prefix_id])
        # Migrate permissions ipmanage -> ipam
        db.execute(
            """
            UPDATE main_permission
            SET name=regexp_replace(name,'^ip:ipmanage:','ip:ipam:')
            WHERE name LIKE 'ip:ipmanage:%%'
            """
        )
        # Migrate ranges
        for name, vrf_id, from_ip, to_ip, description, is_locked, fqdn_action, fqdn_action_parameter in db.execute(
            """
            SELECT name,vrf_id,from_ip,to_ip,description,is_locked,fqdn_action,fqdn_action_parameter
            FROM ip_ipv4addressrange
            """
        ):
            fqdn_template = None
            reverse_nses = None
            if fqdn_action == "G":
                fqdn_template = fqdn_action_parameter
            elif fqdn_action == "D":
                reverse_nses = fqdn_action_parameter
            db.execute(
                """
                INSERT INTO ip_addressrange(name,vrf_id,afi,from_address,to_address,description,is_locked,action,fqdn_template,reverse_nses)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                [
                    name, vrf_id, "4", from_ip, to_ip, description, is_locked,
                    fqdn_action, fqdn_template, reverse_nses
                ]
            )

    def backwards(self):
        pass
