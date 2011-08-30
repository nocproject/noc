# encoding: utf-8
import datetime
from south.db import db
from django.db import models
from django.contrib.contenttypes.management import update_contenttypes
import noc.ip.models

class Migration:

    def forwards(self):
        # VRF Group
        db.execute("UPDATE ip_vrfgroup SET address_constraint='G' WHERE unique_addresses=TRUE")
        # IPv4 Block
        # @todo: migrate tags
        db.execute("""PREPARE ps_get_parent(int,cidr) AS
            SELECT id
            FROM   ip_prefix
            WHERE
                    vrf_id=$1
                AND afi='4'
                AND prefix >> $2
            ORDER BY masklen(prefix) DESC
            LIMIT 1
        """)
        for id,vrf_id,asn_id,prefix,vc_id,description,tt,tags in db.execute("SELECT id,vrf_id,asn_id,prefix,vc_id,description,tt,tags FROM ip_ipv4block ORDER BY prefix"):
            if prefix=="0.0.0.0/0":
                parent_id=None
            else:
                parent_id=db.execute("EXECUTE ps_get_parent(%s,%s)",[vrf_id,prefix])[0][0]
            db.execute("""INSERT INTO ip_prefix(parent_id,vrf_id,afi,prefix,asn_id,vc_id,description,tags,tt)
                VALUES(%s,%s,'4',%s,%s,%s,%s,%s,%s)
                """,[parent_id,vrf_id,prefix,asn_id,vc_id,description,tags,tt])
        # IPv4 Address
        # @todo: migrate tags
        for id,vrf_id,fqdn,ip,description,tt,tags,managed_object_id,auto_update_mac,mac in db.execute("SELECT id,vrf_id,fqdn,ip,description,tt,tags,managed_object_id,auto_update_mac,mac FROM ip_ipv4address ORDER BY ip"):
            prefix_id=db.execute("EXECUTE ps_get_parent(%s,%s)",[vrf_id,ip])[0][0]
            db.execute("""INSERT INTO ip_address(prefix_id,vrf_id,afi,address,fqdn,mac,auto_update_mac,managed_object_id,description,tags,tt)
                VALUES(%s,%s,'4',%s,%s,%s,%s,%s,%s,%s,%s)""",[prefix_id,vrf_id,ip,fqdn,mac,auto_update_mac,managed_object_id,description,tags,tt])
        # PrefixAccess
        db.execute("""INSERT INTO ip_prefixaccess(user_id,vrf_id,afi,prefix,can_view,can_change)
            SELECT user_id,vrf_id,'4',prefix,TRUE,TRUE
            FROM ip_ipv4blockaccess""")
        # Prefix bookmark
        for user_id,vrf_id,prefix in db.execute("""
            SELECT b.user_id,p.vrf_id,p.prefix
            FROM ip_ipv4blockbookmark b JOIN ip_ipv4block p ON (b.prefix_id=p.id)"""):
            prefix_id=db.execute("SELECT id FROM ip_prefix WHERE vrf_id=%s AND prefix=%s AND afi='4'",[vrf_id,prefix])[0][0]
            db.execute("INSERT INTO ip_prefixbookmark(user_id,prefix_id) VALUES(%s,%s)",[user_id,prefix_id])
        # Migrate permissions ipmanage -> ipam
        db.execute("UPDATE main_permission SET name=regexp_replace(name,'^ip:ipmanage:','ip:ipam:') WHERE name LIKE 'ip:ipmanage:%%'")
        # Migrate tags
        update_contenttypes(noc.ip.models,None,interactive=False)
        block_ct_id=db.execute("SELECT id FROM django_content_type WHERE app_label='ip' AND model='ipv4block'")
        if block_ct_id:
            block_ct_id=block_ct_id[0][0]
        address_ct_id=db.execute("SELECT id FROM django_content_type WHERE app_label='ip' AND model='ipv4address'")
        if address_ct_id:
            address_ct_id=address_ct_id[0][0]
        prefix_ct_id=db.execute("SELECT id FROM django_content_type WHERE app_label='ip' AND model='prefix'")[0][0]
        n_address_ct_id=db.execute("SELECT id FROM django_content_type WHERE app_label='ip' AND model='address'")[0][0]
        if block_ct_id:
            tmap={} # IPv4Block.id -> Prefix.id
            for t_id,tag_id,object_id in db.execute("SELECT id,tag_id,object_id FROM tagging_taggeditem WHERE content_type_id=%s",[block_ct_id]):
                try:
                    n_object_id=tmap[object_id]
                except KeyError:
                    n_object_id=db.execute("""SELECT p.id
                        FROM ip_prefix p, ip_ipv4block b
                        WHERE p.vrf_id=b.vrf_id AND p.prefix=b.prefix AND b.id=%s AND p.afi='4'
                        """,[object_id])[0][0]
                    tmap[object_id]=n_object_id
                db.execute("UPDATE tagging_taggeditem SET content_type_id=%s,object_id=%s WHERE id=%s",[prefix_ct_id,n_object_id,t_id])
        
        if address_ct_id:
            tmap={} # IPv4Address.id -> Address.id
            for t_id,tag_id,object_id in db.execute("SELECT id,tag_id,object_id FROM tagging_taggeditem WHERE content_type_id=%s",[address_ct_id]):
                try:
                    n_object_id=tmap[object_id]
                except KeyError:
                    n_object_id=db.execute("""SELECT na.id
                        FROM ip_address na, ip_ipv4address a
                        WHERE na.vrf_id=a.vrf_id AND na.address=a.ip AND a.id=%s AND na.afi='4'
                        """,[object_id])[0][0]
                    tmap[object_id]=n_object_id
                db.execute("UPDATE tagging_taggeditem SET content_type_id=%s,object_id=%s WHERE id=%s",[n_address_ct_id,n_object_id,t_id])
        # Migrate ranges
        for name,vrf_id,from_ip,to_ip,description,is_locked,fqdn_action,fqdn_action_parameter in db.execute("SELECT name,vrf_id,from_ip,to_ip,description,is_locked,fqdn_action,fqdn_action_parameter FROM ip_ipv4addressrange"):
            fqdn_template=None
            reverse_nses=None
            if fqdn_action=="G":
                fqdn_template=fqdn_action_parameter
            elif fqdn_action=="D":
                reverse_nses=fqdn_action_parameter
            db.execute("INSERT INTO ip_addressrange(name,vrf_id,afi,from_address,to_address,description,is_locked,action,fqdn_template,reverse_nses) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[name,vrf_id,"4",from_ip,to_ip,description,is_locked,fqdn_action,fqdn_template,reverse_nses])
    
    def backwards(self):
        pass
    

