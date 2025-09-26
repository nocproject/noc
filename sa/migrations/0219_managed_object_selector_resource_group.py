# ----------------------------------------------------------------------
# ManagedObjectSelector ResourceGroup
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple, defaultdict
from typing import NamedTuple, List, Optional
import bson

# Third-party modules
from pymongo import InsertOne
from noc.core.mongo.connection import get_db

# NOC modules
from noc.core.migration.base import BaseMigration
from noc.core.bi.decorator import bi_hash
from noc.core.validators import is_objectid

selector = namedtuple(
    "MOSSelector",
    [
        "id",
        "name",
        "description",
        "filter_id",
        "filter_name",
        "filter_profile",
        "filter_address",
        "filter_administrative_domain_id",
        "filter_description",
        "filter_prefix_id",
        "filter_object_profile_id",
        "filter_vrf_id",
        "filter_vc_domain_id",
        "filter_pool",
        "filter_vendor",
        "filter_platform",
        "filter_version",
        "filter_tt_system",
        "filter_labels",
        "source_combine_method",
    ],
)
BULK = 10000


class ManagedObjectSelectorLabels(object):
    """
    Class for convert ManagedObjectSelector Fields to Labels set
    """

    field_map = {
        "filter_profile": {"collection": "noc.profiles", "category": "profile"},
        "filter_prefix_id": {"table": "main_prefixtable", "category": "prefixfilter"},
        "filter_object_profile_id": {
            "table": "sa_managedobjectprofile",
            "category": "managedobjectprofile",
        },
        "filter_vrf_id": {"table": "ip_vrf", "category": "ipvrf"},
        "filter_vc_domain_id": {"table": "vc_vcdomain", "category": "vcdomain"},
        "filter_pool": {"collection": "noc.pools", "category": "pool"},
        "filter_vendor": {"collection": "noc.vendors", "category": "vendor"},
        "filter_platform": {"collection": "noc.platforms", "category": "platform"},
        "filter_tt_system": {"collection": "noc.ttsystem", "category": "ttsystem"},
    }

    def __init__(self):
        self.profiles = {}
        self.regex_label = {}
        self.regex_bulk = []

    @classmethod
    def get_cursor(cls):
        """
        Get PostgreSQL cursor
        :return:
        """
        if not hasattr(cls, "_cursor"):
            from django.db import connection

            cls._cursor = connection.cursor()
        return cls._cursor

    @staticmethod
    def get_match_label(category, name, op="=", matched_scope=""):
        if matched_scope:
            matched_scope += "::"
        return f"noc::{category}::{name}::{matched_scope}{op}"

    @classmethod
    def get_mongo_name_by_id(cls, collection, oid: str) -> Optional[str]:
        coll = get_db()[collection]
        if not is_objectid(oid):
            print(f"[migrate_object_selector_resource] Unknown OID {oid}")
            return None
        r = coll.find_one({"_id": bson.ObjectId(oid)}, {"name": 1})
        if not r:
            return None
        return r["name"]

    @classmethod
    def get_pg_name_by_id(cls, table, oid: str) -> Optional[str]:
        cursor = cls.get_cursor()
        cursor.execute(f"SELECT name FROM {table} WHERE id = %s", [oid])
        r = cursor.fetchall()
        if not r:
            return None
        (name,) = r[0]
        return name

    def get_field_label(self, field_name: str, field_value: str):
        if hasattr(self, field_name):
            return getattr(self, field_name)(field_value)
        if field_name in self.field_map:
            f_map = self.field_map[field_name]
            name = None
            if "table" in f_map:
                name = self.get_pg_name_by_id(f_map["table"], field_value)
            elif "collection" in f_map:
                name = self.get_mongo_name_by_id(f_map["collection"], field_value)
            if name:
                if f_map["category"] == "prefixfilter":
                    # For PrefixList Match label
                    return self.get_match_label(f_map["category"], name, op="<")
                return self.get_match_label(f_map["category"], name)
        return None

    def get_regex_label(self, regex, field, selector_name):
        coll = get_db()["labels"]
        scope = "managedobject_name"
        if field == "filter_address":
            scope = "managedobject_address"
        elif field == "filter_description":
            scope = "managedobject_description"
        r = coll.find_one(
            {"match_regex": {"$elemMatch": {"regexp": regex, "scope": scope}}}, {"name": 1}
        )
        if r:
            return r["name"]
        # Create RegexLabel
        name = f"SM_{selector_name}_{field}"
        self.regex_bulk += [
            InsertOne(
                {
                    # "_id": bson.ObjectId(),
                    "name": name,
                    "description": f"Migrate MangedObjectSelector {selector_name}, for field {field}",
                    "bg_color1": 8359053,
                    "fg_color1": 16777215,
                    "bg_color2": 8359053,
                    "fg_color2": 16777215,
                    "is_protected": False,
                    "is_regex": True,
                    # Label scope
                    "enable_agent": False,
                    "enable_service": False,
                    "enable_serviceprofile": False,
                    "enable_managedobject": True,
                    "enable_managedobjectprofile": False,
                    "enable_administrativedomain": False,
                    "enable_authprofile": False,
                    "enable_commandsnippet": False,
                    # Exposition scope
                    "expose_metric": False,
                    "expose_datastream": False,
                    "match_regex": [
                        {
                            "regexp": regex,
                            "flag_multiline": False,
                            "flag_dotall": False,
                            "scope": scope,
                        }
                    ],
                }
            )
        ]
        return name

    def filter_administrative_domain_id(self, ad_id):
        name = self.get_pg_name_by_id("sa_administrativedomain", ad_id)
        if not name:
            return None
        return self.get_match_label("adm_domain", name, op="<")

    def get_labels(self, sel: NamedTuple) -> List[str]:
        r = []
        for f_name in sel._fields:
            if f_name in {"id", "name", "description", "source_combine_method"}:
                continue
            f_value = getattr(sel, f_name)
            if not f_value:
                continue
            if f_name in {"filter_name", "filter_address", "filter_description"}:
                label = self.get_regex_label(f_value, f_name, sel.name)
            elif f_name == "filter_labels":
                r += f_value
                continue
            else:
                label = self.get_field_label(f_name, f_value)
            if label:
                r += [label]
        return r


class Migration(BaseMigration):
    """
    selector -> labels
    selector -> ManagedObject
    field -> label_wildcard
    label_wildcard -> [labels]
    1. Crate labels for classifiactions
    2. Create filter
    3. Create ResourceGroup with Match Rules
    4. Fill ResourceGroup to ManagedOject Client Group
    """

    migrate_map = defaultdict(dict)

    def migrate(self):
        sources_map = defaultdict(list)
        for sel_from, sel_to in self.db.execute(
            """
                SELECT from_managedobjectselector_id, to_managedobjectselector_id
                FROM sa_managedobjectselector_sources
                """
        ):
            sources_map[sel_from] += [sel_to]
        # Fix more than two level
        for sel_id in list(sources_map):
            for fid in list(sources_map[sel_id]):
                if fid in sources_map:
                    sources_map[sel_id].remove(fid)
                    sources_map[sel_id] += sources_map[fid]
        mosl = ManagedObjectSelectorLabels()
        match_labels = defaultdict(set)
        # Main Loop
        for r in self.db.execute(
            """
                SELECT
                 id,
                 name,
                 description,
                 filter_id,
                 filter_name,
                 filter_profile,
                 filter_address,
                 filter_administrative_domain_id,
                 filter_description,
                 filter_prefix_id,
                 filter_object_profile_id,
                 filter_vrf_id,
                 filter_vc_domain_id,
                 filter_pool,
                 filter_vendor,
                 filter_platform,
                 filter_version,
                 filter_tt_system,
                 filter_labels,
                 source_combine_method
                FROM sa_managedobjectselector
                """
        ):
            ss = selector(*r)
            self.migrate_map[r[0]]["selector"] = ss
            if ss.id in sources_map:
                self.migrate_map[r[0]]["match_rules"] = []
                continue
            labels = mosl.get_labels(ss)
            for ll in labels:
                match_labels[ll].add("")
            self.migrate_map[r[0]]["match_rules"] = [labels] if labels else []
        # Apply RegexLabels
        if mosl.regex_bulk:
            coll = self.mongo_db["labels"]
            coll.bulk_write(mosl.regex_bulk)
        # Apply Sources MAP
        for sel_id, sources in sources_map.items():
            for source in sources:
                self.migrate_map[sel_id]["match_rules"] += self.migrate_map[source]["match_rules"]
        self.sync_resource_group()
        # Sync ManagedObject
        self.sync_managedobject()
        # Sync Labels
        self.sync_labels(match_labels)

    def sync_resource_group(self):
        rcid = bson.ObjectId()
        bulk = [
            InsertOne(
                {
                    "_id": rcid,
                    "name": "Managed Object Selectors",
                    "parent": None,
                    "description": "Migrate from ManagedObjectSelectors",
                    "technology": bson.ObjectId("5b6d6819d706360001a0b716"),  # "Object Group"
                    "dynamic_service_labels": [],
                    "dynamic_client_labels": [],
                    "bi_id": bson.Int64(bi_hash(rcid)),
                    "labels": [],
                    "effective_labels": [],
                }
            )
        ]
        l_coll = self.mongo_db["resourcegroups"]
        for sel_id, rules in self.migrate_map.items():
            sel, match_rules = rules["selector"], rules["match_rules"]
            cid = bson.ObjectId()
            bulk.append(
                InsertOne(
                    {
                        "_id": cid,
                        "name": f"MOS {sel.name}",
                        "parent": rcid,
                        "description": f"Migrate from ManagedObjectSelector {sel.name}",
                        "technology": bson.ObjectId("5b6dbbefd70636000170b980"),  # "Object Group"
                        "dynamic_service_labels": [{"labels": m} for m in match_rules],
                        "dynamic_client_labels": [],
                        "bi_id": bson.Int64(bi_hash(cid)),
                        "labels": [],
                        "effective_labels": [],
                    }
                )
            )
            self.migrate_map[sel_id]["resource_group"] = str(cid)
        if bulk:
            l_coll.bulk_write(bulk)

    def sync_managedobject(self):
        updating_object = defaultdict(set)
        for cache in self.mongo_db["noc.cache.selector"].find():
            o_id, s_id = cache["object"], cache["selector"]
            if "resource_group" not in self.migrate_map[s_id]:
                continue
            updating_object[self.migrate_map[s_id]["resource_group"]].add(o_id)

        for rg in updating_object:
            mos = list(updating_object[rg])
            while mos:
                chunk, mos = mos[:BULK], mos[BULK:]
                self.db.execute(
                    """
                 UPDATE sa_managedobject
                 SET effective_service_groups = array_append(effective_service_groups, %s)
                 WHERE id = ANY(ARRAY[%s]::INT[])
                """,
                    [rg, chunk],
                )

    def sync_labels(self, labels):
        # Create labels
        bulk = []
        l_coll = self.mongo_db["labels"]
        current_labels = {ll["name"]: ll["_id"] for ll in l_coll.find()}
        for label in labels:
            if label in current_labels:
                continue
            doc = {
                # "_id": bson.ObjectId(),
                "name": label,
                "description": "",
                "bg_color1": 8359053,
                "fg_color1": 16777215,
                "bg_color2": 8359053,
                "fg_color2": 16777215,
                "is_protected": False,
                # Label scope
                "enable_agent": False,
                "enable_service": False,
                "enable_serviceprofile": False,
                "enable_managedobject": False,
                "enable_managedobjectprofile": False,
                "enable_administrativedomain": False,
                "enable_authprofile": False,
                "enable_commandsnippet": False,
                # Exposition scope
                "expose_metric": False,
                "expose_datastream": False,
            }
            bulk += [InsertOne(doc)]
        if bulk:
            l_coll.bulk_write(bulk, ordered=True)
