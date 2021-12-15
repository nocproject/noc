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


class Migration(BaseMigration):
    depends_on = [("sa", "0223_managed_object_l2domain")]

    def migrate(self):
        # Create default VLAN Profile
        vlan_prof_id = bson.ObjectId()
        self.mongo_db["vlanprofiles"].insert_one(
            {
                "_id": vlan_prof_id,
                "name": "default",
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "labels": [],
                "effective_labels": [],
                "bi_id": bson.Int64(bi_hash(vlan_prof_id)),
            }
        )
        # Create default L2 Domain Profile
        l2d_prof_id = bson.ObjectId()
        self.mongo_db["l2domainprofiles"].insert_one(
            {
                "_id": l2d_prof_id,
                "name": "default",
                "workflow": bson.ObjectId("5a01d980b6f529000100d37a"),
                "pools": [],
                "labels": [],
                "effective_labels": [],
                "bi_id": bson.Int64(bi_hash(l2d_prof_id)),
                "vlan_discovery_filter": vlan_prof_id,
                "vlan_discovery_policy": "E",
            }
        )
        # Create default L2 Domain
        l2dom_id = bson.ObjectId()
        self.mongo_db["l2domains"].insert_one(
            {
                "_id": l2dom_id,
                "name": "default",
                "description": "Default L2 Domain Profile",
                "profile": l2d_prof_id,
                "pools": [],
                "labels": [],
                "effective_labels": [],
                "bi_id": bson.Int64(bi_hash(l2dom_id)),
            }
        )
        # Check VC - if count more 0 - migrate VC
        (vc_count,) = self.db.execute(
            """
            SELECT count(*)
            FROM vc_vc
            WHERE l1 != 1
            """
        )
        # VC Migration
        if vc_count:
            self.vc_migrate(l2d_prof_id, vlan_prof_id)
        # VLAN Migration
        vlans = self.mongo_db["vlans"].count({"vlan": {"$ne": 1}})
        if not vc_count and vlans:
            self.vlan_mirate(l2d_prof_id)

    def vlan_mirate(self, default_l2d_profile_id):
        v_coll = self.mongo_db["vlans"]
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
            {"_id": {"$id": segments}}
        ):
            l2dom_id = bson.ObjectId()
            l2_domains += [
                InsertOne(
                    {
                        "_id": l2dom_id,
                        "name": name,
                        "description": description,
                        "profile": default_l2d_profile_id,
                        "pools": [],
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(l2dom_id)),
                    }
                )
            ]
            vlans_update += [UpdateMany({"segment": nsid}, {"$set": {"l2_domain": l2dom_id}})]
            l2_domain_map[nsid] = l2dom_id
        if l2_domains:
            self.mongo_db["l2domains"].bulk_write(l2_domains)
        if vlans_update:
            v_coll.bulk_write(vlans_update)
        # Update ManagedObject L2 Domain
        for ns_id, l2_d in l2_domain_map.items():
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET l2_domain = '%s'
                WHERE segment = '%s'
                """,
                [str(l2_d), str(ns_id)],
            )

    def vc_migrate(self, default_l2d_profile_id, default_vlan_profile):
        # Clean VLANs collection
        self.mongo_db["vlans"].remove({})
        l2_domains = []
        l2_domain_map = {}
        for vid, name, description in self.db.execute(
            """
            SELECT id, name, description
            FROM vc_vcdomain
            WHERE name != 'default'
            """
        ):
            l2dom_id = bson.ObjectId()
            l2_domain_map[vid] = l2dom_id
            l2_domains += [
                InsertOne(
                    {
                        "_id": l2dom_id,
                        "name": name,
                        "description": description,
                        "profile": default_l2d_profile_id,
                        "pools": [],
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(l2dom_id)),
                    }
                )
            ]
        if l2_domains:
            self.mongo_db["l2domains"].bulk_write(l2_domains)
        vlans = []
        # VLAN Migration
        for vid, vc_domain, name, description in self.db.execute(
            """
            SELECT l2, vc_domain, name, description
            FROM vc_vc
            WHERE l1 != 1
            """
        ):
            vid = bson.ObjectId()
            vlans += [
                InsertOne(
                    {
                        "_id": vid,
                        "name": "Data1",
                        "profile": default_vlan_profile,
                        "vlan": 3,
                        "l2_domain": l2_domain_map.get(vc_domain, default_l2d_profile_id),
                        "labels": [],
                        "effective_labels": [],
                        "bi_id": bson.Int64(bi_hash(vid)),
                        "expired": None,
                        "state": bson.ObjectId("5a17f61b1bb6270001bd0328"),
                    }
                )
            ]
        if vlans:
            # @todo Chunk
            self.mongo_db["vlans"].bulk_write(vlans)
        # Update ManagedObject L2 Domain
        for vid, l2_d in l2_domain_map.items():
            self.db.execute(
                """
                UPDATE sa_managedobject
                SET l2_domain = '%s'
                WHERE vc_domain_id = %s
                """,
                [str(l2_d), vid],
            )
