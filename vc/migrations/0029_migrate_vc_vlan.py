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
DEFAULT_L2_DOMAIN_ID = bson.ObjectId("61bee7425c42c21338453614")


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
        vlan_profiles_count = self.mongo_db["vlanprofiles"].count_documents({})
        # VC Migration
        # l2domain_profile_id = bson.ObjectId("61bee6f45c42c21338453613")
        l2domain_profile_id = self.mongo_db["l2domainprofiles"].find_one(
            {"name": "default"}, {"_id": 1}
        )["_id"]
        # vlan_profile_id = bson.ObjectId("61bffba63adaa22083f2abfc")
        vlan_profile_id = self.mongo_db["vlanprofiles"].find_one({"name": "default"}, {"_id": 1})[
            "_id"
        ]
        vc_migrate = False
        if vc_count and not vlan_profiles_count > 2:
            self.vc_migrate(l2domain_profile_id, vlan_profile_id)
            vc_migrate = True
        # VLAN Migration
        vlans = self.mongo_db["vlans"].count_documents({"vlan": {"$ne": 1}})
        if not vc_migrate and vlans:
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
            return
        l2_domains = []
        vlans_update = []
        l2_domain_map = {}
        # NetworkSegment migrate to L2 Domain
        for segment in self.mongo_db["noc.networksegments"].find({"_id": {"$in": segments}}):
            l2domain_id = bson.ObjectId()
            l2_domains += [
                InsertOne(
                    {
                        "_id": l2domain_id,
                        "name": segment["name"],
                        "description": segment.get("description", ""),
                        "profile": default_l2d_profile_id,
                        "pools": [],
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(l2domain_id)),
                    }
                )
            ]
            nsid = segment["_id"]
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
        v_coll.delete_many({})
        l2_domains = []
        l2_domain_map = {1: DEFAULT_L2_DOMAIN_ID}
        for vid, name, description in self.db.execute(
            """
            SELECT id, name, description
            FROM vc_vcdomain
            WHERE id != 1
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
        processed_vlans = set()
        # VC -> VLAN Migration
        for v_num, v_name, vc_domain_id, name, description in self.db.execute(
            """
            SELECT l1, name, vc_domain_id, name, description
            FROM vc_vc
            WHERE l1 != 1 and l2 != 1
            """
        ):
            if vc_domain_id not in l2_domain_map:
                print(f"Unknown VC Domain: {vc_domain_id}")
                continue
            l2_domain_id = l2_domain_map.get(vc_domain_id, DEFAULT_L2_DOMAIN_ID)
            if (l2_domain_id, v_num) in processed_vlans:
                print(f"Duplicate VLAN number on domain: {vc_domain_id}")
                continue
            vlan_id = bson.ObjectId()
            vlans += [
                InsertOne(
                    {
                        "_id": vlan_id,
                        "name": v_name,
                        "profile": default_vlan_profile,
                        "vlan": v_num,
                        "l2_domain": l2_domain_id,
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(vlan_id)),
                        "expired": None,
                        "state": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                    }
                )
            ]
            processed_vlans.add((l2_domain_id, v_num))
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
