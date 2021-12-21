# ----------------------------------------------------------------------
# Migrate VC to VLAN
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details

# Third-party modules
import bson
from pymongo import InsertOne, UpdateMany

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash

CHUNK = 500


class Migration(BaseMigration):
    depends_on = [("sa", "0223_managed_object_l2domain")]

    def migrate(self):
        # Create default VLAN Profile
        # Check VC - if count more 0 - migrate VC
        ((vc_count,),) = self.db.execute(
            """
            SELECT count(*)
            FROM vc_vc
            WHERE l1 != 1
            """
        )
        # VC Migration
        l2domain_profile_id = bson.ObjectId("61bee7425c42c21338453614")
        vlan_profile_id = bson.ObjectId("61bffba63adaa22083f2abfc")
        if vc_count:
            self.vc_migrate(l2domain_profile_id, vlan_profile_id)
        # VLAN Migration
        vlans = self.mongo_db["vlans"].count_documents({"vlan": {"$ne": 1}})
        if not vc_count and vlans:
            self.vlan_migrate(l2domain_profile_id)

    def vlan_migrate(self, default_l2d_profile_id):
        v_coll = self.mongo_db["vlans"]
        v_coll.drop_indexes()
        # VLAN Segments
        segments = [
            s["_id"]
            for s in v_coll.aggregate([{"$group": {"_id": "$segment", "count": {"$sum": 1}}}])
        ]
        if not segments:
            #
            return
        l2_domains = []
        vlans_update = []
        l2_domain_map = {}
        # NetworkSegment migrate to L2 Domain
        for nsid, name, description in self.mongo_db["noc.networksegments"].find(
            {"_id": {"$in": segments}}
        ):
            l2domain_id = bson.ObjectId()
            l2_domains += [
                InsertOne(
                    {
                        "_id": l2domain_id,
                        "name": name,
                        "description": description,
                        "profile": default_l2d_profile_id,
                        "pools": [],
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(l2domain_id)),
                    }
                )
            ]
            vlans_update += [UpdateMany({"segment": nsid}, {"$set": {"l2_domain": l2domain_id}})]
            l2_domain_map[nsid] = l2domain_id
        if l2_domains:
            self.mongo_db["l2domains"].bulk_write(l2_domains)
        if vlans_update:
            v_coll.bulk_write(vlans_update)
        # Update ManagedObject L2 Domain
        for ns_id, l2_d in l2_domain_map.items():
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET l2_domain = %s
                WHERE segment = %s
                """,
                [str(l2_d), str(ns_id)],
            )

    def vc_migrate(self, default_l2d_profile_id, default_vlan_profile):
        # Clean VLANs collection
        v_coll = self.mongo_db["vlans"]
        v_coll.drop_indexes()
        v_coll.remove({})
        l2_domains = []
        l2_domain_map = {}
        for vid, name, description in self.db.execute(
            """
            SELECT id, name, description
            FROM vc_vcdomain
            WHERE name != 'default'
            """
        ):
            l2domain_id = bson.ObjectId()
            l2_domain_map[vid] = l2domain_id
            l2_domains += [
                InsertOne(
                    {
                        "_id": l2domain_id,
                        "name": name,
                        "description": description,
                        "profile": default_l2d_profile_id,
                        "pools": [],
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(l2domain_id)),
                    }
                )
            ]
        if l2_domains:
            self.mongo_db["l2domains"].bulk_write(l2_domains)
        vlans = []
        # VC -> VLAN Migration
        for v_num, vc_domain, name, description in self.db.execute(
            """
            SELECT l2, vc_domain_id, name, description
            FROM vc_vc
            WHERE l1 != 1
            """
        ):
            vlan_id = bson.ObjectId()
            vlans += [
                InsertOne(
                    {
                        "_id": vlan_id,
                        "name": "Data1",
                        "profile": default_vlan_profile,
                        "vlan": v_num,
                        "l2_domain": l2_domain_map.get(vc_domain, default_l2d_profile_id),
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(vlan_id)),
                        "expired": None,
                        "state": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                    }
                )
            ]
        if len(vlans) > CHUNK:
            self.mongo_db["vlans"].bulk_write(vlans)
            vlans = []
        if vlans:
            self.mongo_db["vlans"].bulk_write(vlans)
        # Update ManagedObject L2 Domain
        for vid, l2_d in l2_domain_map.items():
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET l2_domain = %s
                WHERE vc_domain_id = %s
                """,
                [str(l2_d), vid],
            )
