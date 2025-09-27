# ----------------------------------------------------------------------
# Migrate Interface Classification Rules to labels
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
from typing import Optional, List, Dict, Any
import bson
from collections import defaultdict

# Third-party modules
from pymongo import InsertOne, UpdateOne

# NOC modules
from noc.core.mongo.connection import get_db
from noc.core.migration.base import BaseMigration


class InterfaceClassifierLabels(object):
    """
    Class for convert ManagedObjectSelector Fields to Labels set
    """

    def __init__(self):
        self.profiles = {}
        self.regex_label = {}
        self.regex_bulk = []
        self.new_vcfilters = set()
        self.new_prefixes = set()
        self.duplicate_counter = 0
        self.proccessed_regex = set()

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

    def get_regex_label(self, regex, field, rule_name):
        coll = get_db()["labels"]
        scope = "interface_name"
        if field == "description":
            scope = "interface_description"
        if (scope, regex) in self.regex_label:
            return self.regex_label[(scope, regex)]
        r = coll.find_one(
            {"match_regex": {"$elemMatch": {"regexp": regex, "scope": scope}}}, {"name": 1}
        )
        if r:
            name = r["name"]
        else:
            # Create RegexLabel
            name = f"IC_{rule_name}_{field}"
            if name in self.proccessed_regex:
                name += f" {self.duplicate_counter}"
            self.proccessed_regex.add(name)
            self.regex_bulk += [
                InsertOne(
                    {
                        # "_id": bson.ObjectId(),
                        "name": name,
                        "description": f"Migrate InterfaceClassifiaction {rule_name}, for field {field}",
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
                        "enable_managedobject": False,
                        "enable_managedobjectprofile": False,
                        "enable_administrativedomain": False,
                        "enable_interface": True,
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
        self.regex_label[(scope, regex)] = name
        return name

    def filter_regex(self, field, op, value, rule_name=None):
        if op == "regexp":
            return self.get_regex_label(value, field, rule_name)
        if op == "eq":
            return self.get_regex_label(f"^{value}$", field, rule_name)
        return None

    def filter_address(self, field, op, value, prefix, rule_name: Optional[str] = None):
        if op == "in" and prefix:
            name = self.get_pg_name_by_id("main_prefixtable", prefix)
            if not name:
                return None
            return self.get_match_label("prefixfilter", name, op="<")
        if op == "eq" and value:
            name = (f"Migrate InterfaceClassifiaction {rule_name}, for field {field}",)
            self.new_vcfilters.add((name, value))
            return self.get_match_label("prefixfilter", name, matched_scope=field, op="=")
        return None

    def filter_vlan(self, field, op, value, vlan_filter, rule_name: Optional[str] = None):
        if op == "in" and vlan_filter:
            name = self.get_pg_name_by_id("vc_vcfilter", vlan_filter)
            if not name:
                return None
            return self.get_match_label("vcfilter", name, matched_scope=field, op="&")
        if op == "eq" and value:
            name = (f"Migrate IC {rule_name}, for field {field}"[:60],)
            self.new_vcfilters.add((name, value))
            return self.get_match_label("vcfilter", name, matched_scope=field, op="=")
        return None

    def get_labels(
        self, match_rules: List[Dict[str, Any]], rule_name: Optional[str] = None
    ) -> List[str]:
        """

        :param match_rules:
        :param rule_name:
        :return:
        """
        r = []
        for rule in match_rules:
            self.duplicate_counter += 1
            field, op, value = rule["field"], rule["op"], rule.get("value")
            if field == "ip":
                label = self.filter_address(field, op, value, rule.get("prefix_table"), rule_name)
            elif field in ["tagged", "untagged"]:
                label = self.filter_vlan(field, op, value, rule.get("vc_filter"), rule_name)
            elif field == "hints" and value:
                label = value
            else:
                label = self.filter_regex(field, op, value, rule_name)
            if label:
                r += [label]
        return r


class Migration(BaseMigration):
    depends_on = [("sa", "0219_managed_object_selector_resource_group")]

    def migrate(self):
        profile_rules = defaultdict(list)
        match_labels = defaultdict(set)
        icrl = InterfaceClassifierLabels()
        # profile -> rules [{"order" , labels, }]
        selectors_label = {
            r[0]: f"noc::resourcegroup::{r[1]}::="
            for r in self.db.execute(
                """
                    SELECT
                     id,
                     name
                    FROM sa_managedobjectselector
                    """
            )
        }
        # ServiceProfile Rules
        coll = self.mongo_db["noc.serviceprofiles"]
        for profile in coll.find({"interface_profile": {"$exists": True}}):
            profile_rules[profile["interface_profile"]] += [
                {
                    "order": 5,
                    "description": "",
                    "mlabels": [f'noc::serviceprofile::{profile["name"]}::='],
                }
            ]
        # Main loop
        coll = self.mongo_db["noc.inv.interfaceclassificationrules"]
        for rule in coll.find():
            if "match" not in rule:
                continue
            m_labels = set()
            m_labels.add(selectors_label[rule["selector"]])
            m_labels |= set(icrl.get_labels(rule["match"], rule["name"]))
            profile_rules[rule["profile"]] += [
                {
                    "order": rule.get("order", 1) if rule["is_active"] else 0,
                    "description": rule.get("description"),
                    "mlabels": m_labels,
                }
            ]
            for ll in m_labels:
                match_labels[ll].add("")
        # Apply RegexLabels
        if icrl.regex_bulk:
            coll = self.mongo_db["labels"]
            coll.bulk_write(icrl.regex_bulk)
        if icrl.new_vcfilters:
            # Migrate VCFilter
            for name, value in icrl.new_vcfilters:
                self.db.execute(
                    """
                        INSERT INTO vc_vcfilter(name, expression) VALUES(%s, %s)
                        """,
                    [name, value],
                )

        coll = self.mongo_db["noc.interface_profiles"]
        bulk = []
        for profile, rules in profile_rules.items():
            bulk += [
                UpdateOne(
                    {"_id": profile},
                    {
                        "$set": {
                            "dynamic_classification_policy": "R",
                            "match_rules": [
                                {"dynamic_order": rule["order"], "labels": list(rule["mlabels"])}
                                for rule in rules
                            ],
                        }
                    },
                )
            ]
        if bulk:
            coll.bulk_write(bulk)
        # Sync Labels
        self.sync_labels(match_labels)

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
